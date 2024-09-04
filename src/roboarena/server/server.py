import logging
from collections import deque
from collections.abc import Collection
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from bidict import bidict
from pygame import Color
from pygame.time import Clock

from roboarena.server.entity import (
    ServerEnemyRobot,
    ServerInputHandler,
    ServerPlayerRobot,
)
from roboarena.server.events import EventBuffer, EventName
from roboarena.server.level_generation.level_generator import (
    LevelGenerator,
    LevelUpdate,
)
from roboarena.server.level_generation.tileset import tileset
from roboarena.server.room import Room
from roboarena.shared.block import floor_door, floor_room_spawn, room_blocks
from roboarena.shared.constants import EnemyConstants, NetworkConstants, PlayerConstants
from roboarena.shared.custom_threading import Atom
from roboarena.shared.game import GameState as SharedGameState
from roboarena.shared.network import IpV4, Network, Receiver
from roboarena.shared.time import get_time
from roboarena.shared.types import (
    Acknoledgement,
    ClientConnectionRequestEvent,
    ClientGameEvent,
    ClientId,
    ClientInputEvent,
    ClientLobbyReadyEvent,
    Dispatch,
    EntityId,
    EventType,
    Marker,
    ServerConnectionConfirmEvent,
    ServerDeleteEntityEvent,
    ServerEntityEvent,
    ServerEntityType,
    ServerGameEvent,
    ServerGameEventType,
    ServerGameStartEvent,
    ServerLevelUpdateEvent,
    ServerMarkerEvent,
    StartFrameEvent,
    Time,
    basic_weapon,
)
from roboarena.shared.util import (
    EventTarget,
    Stoppable,
    Stopped,
    flatten,
    gen_id,
    neighbours_4,
    search_connected,
    square_space_around,
)
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import Level

logger = logging.getLogger(__name__)


class LobbyState:
    @dataclass
    class ClientInfo:
        ip: IpV4
        ready: bool

    _logger = logging.getLogger(f"{__name__}.LobbyState")
    _server: "Server"
    _clients: dict[ClientId, ClientInfo]

    def __init__(self, server: "Server") -> None:
        self._server = server
        self._clients = {}

    def handle(self, t_msg: Time, msg: EventType) -> None:
        match msg:
            case ClientConnectionRequestEvent(ip):
                client_id = gen_id(self._clients.keys())
                self._clients[client_id] = LobbyState.ClientInfo(ip, False)
                self._server.network.send(ip, ServerConnectionConfirmEvent(client_id))
            case ClientLobbyReadyEvent(client_id):
                self._clients[client_id].ready = True
            case _:
                self._logger.error(f"Unexpected event: {msg}")

    def loop(self) -> dict[EntityId, IpV4] | Stopped:
        logger.debug("enter LobbyState.loop")
        while len(self._clients) == 0 or not all(
            _.ready for _ in self._clients.values()
        ):
            if self._server.stopped.get():
                return Stopped()
            for t_msg, msg in self._server.receiver.receive():
                self.handle(t_msg, msg)
        self._logger.debug(f"close lobby with clients {self._clients}")
        return {client_id: client.ip for client_id, client in self._clients.items()}


class GameState(SharedGameState):
    @dataclass
    class ClientInfo:
        ip: IpV4
        last_ack: Acknoledgement
        entity_id: EntityId
        entity: ServerInputHandler
        events: EventBuffer[ServerGameEventType] = field(
            default_factory=EventBuffer, init=False
        )

    _logger = logging.getLogger(f"{__name__}.GameState")
    _server: "Server"
    _clients: dict[ClientId, ClientInfo]
    env = "server"
    entities: bidict[EntityId, ServerEntityType]
    _rooms: list[Room]
    markers: deque[Marker]
    _deleted_entities: list[ServerEntityType]
    _created_entities: list[ServerEntityType]

    _level_gen: LevelGenerator

    def __init__(self, server: "Server", clients: dict[ClientId, IpV4]) -> None:
        self._server = server
        self._clients = {}
        self.entities = bidict()  # type: ignore
        self._rooms = list()

        self._logger.debug(f"initialize with clients: {clients}")

        self._level_gen = LevelGenerator(tileset)
        enemy_id = 0
        enemy = ServerEnemyRobot(
            self,
            EnemyConstants.START_HEALTH,
            (Vector(10.0, 1.0), Vector(1.0, 0.0)),
            Color(255, 0, 0),
            basic_weapon,
        )
        self.entities[enemy_id] = enemy
        self.markers = deque(maxlen=1000)
        self.events = EventTarget()

        for client_id, ip in clients.items():
            entity_id, entity = self.gen_client_entity()
            self._clients[client_id] = GameState.ClientInfo(
                ip, NetworkConstants.INITIAL_ACKNOLEDGEMENT, entity_id, entity
            )
            self.entities[entity_id] = entity

        self._logger.debug(f"initialized entities: {self.entities}")

        spawn_events = [e.to_event(i) for i, e in self.entities.items()]
        for client in self._clients.values():
            level = self._level_gen.level
            event = ServerGameStartEvent(client.entity_id, spawn_events, level)
            self._server.network.send(client.ip, event)

    @property
    def level(self) -> "Level":  # type: ignore
        return self._level_gen.level

    def create_entity(self, entity: ServerEntityType) -> None:
        self._created_entities.append(entity)

    def _create_entity(self, entity: ServerEntityType) -> None:
        entity_id = gen_id(self.entities.keys())
        self.entities[entity_id] = entity
        self._dispatch(None, f"create-entity/{entity_id}", entity.to_event(entity_id))

    def delete_entity(self, entity: ServerEntityType) -> None:
        self._deleted_entities.append(entity)

    def _delete_entity(self, entity: ServerEntityType) -> None:
        entity_id = self.entities.inverse[entity]
        del self.entities[entity_id]
        event = ServerDeleteEntityEvent(entity_id)
        self._dispatch(None, f"delete-entity/{entity_id}", event)

    def create_rooms(self, update: LevelUpdate) -> None:
        for pos, block in update:
            if block is not floor_room_spawn:
                continue
            room = search_connected(
                pos,
                self._level_gen.level,
                lambda b: b if b in room_blocks else None,
                neighbours_4,
            )
            floors = {p for p, b in room.items() if b is not floor_door}
            doors = {p for p, b in room.items() if b is floor_door}
            self._rooms.append(Room(self, floors, doors))

    def dispatch_factory(
        self, client: Optional[ClientId], entity: EntityId
    ) -> Dispatch[object]:
        SEE = ServerEntityEvent
        return lambda n, e: self._dispatch(client, f"{entity}/{n}", SEE(entity, n, e))

    def dispatch(self, entity: ServerEntityType, event_name: EventName, event: object):
        """Method for entities to call directly

        Instead of creating a wrapper using `dispatch-factory` and passing it
        down explicitly the entities can call this method and pass themselves.
        """
        entity_id = self.entities.inverse[entity]
        see = ServerEntityEvent(entity_id, event_name, event)
        self._dispatch(None, f"{entity_id}/{event_name}", see)

    def _dispatch(
        self,
        client: Optional[ClientId],
        event_name: EventName,
        event: ServerGameEventType,
    ):
        targets_ids = [client] if client is not None else self._clients.keys()
        for target_id in targets_ids:
            target = self._clients[target_id]
            target.events.dispatch(event_name, event)

    def handle(self, t_msg: Time, msg: EventType) -> None:
        match msg:
            case ClientGameEvent(client_id, ack, event):
                self._clients[client_id].last_ack = ack
                match event:
                    case ClientInputEvent(input, dt):
                        self._clients[client_id].entity.on_input(input, dt, t_msg)
            case _:
                self._logger.error(f"Unexpected event: {msg}")
                raise ValueError(f"Unexpected event: {msg}")

    def gen_client_entity(self) -> tuple[EntityId, ServerPlayerRobot]:
        entity_id = gen_id(self.entities.keys())
        entity = ServerPlayerRobot(
            self,
            PlayerConstants.START_HEALTH,
            (Vector(12.5, 12.5), Vector(1.0, 0.0)),
            Color(0, 255, 0),
            self.dispatch_factory(None, entity_id),
        )
        return (entity_id, entity)

    def mark(self, markers: Marker | Collection[Marker]):
        markers = markers if isinstance(markers, Collection) else [markers]
        self.markers += markers
        self._dispatch(None, f"marker/{uuid4()}", ServerMarkerEvent(markers))

    def loop(self) -> Stopped:
        last_t = get_time()
        clock = Clock()

        while True:
            if self._server.stopped.get():
                return Stopped()

            # init update
            t_update = get_time()
            dt_update = t_update - last_t
            dt_frame = dt_update / NetworkConstants.SERVER_FRAMES_PER_TIMESTEP

            self.events.dispatch(StartFrameEvent())

            # Each update is split into 3 frames to get more precise results
            for i in range(NetworkConstants.SERVER_FRAMES_PER_TIMESTEP):
                t_frame = last_t + i * dt_frame

                # TODO: create/delete_entitiy into loop function using a TickCtx
                self._created_entities = list()
                self._deleted_entities = list()

                # generate level
                players = (c.entity.position for c in self._clients.values())
                near_players = flatten(square_space_around(p, 10) for p in players)
                level_update = self._level_gen.generate(near_players)
                level_update_evt = ServerLevelUpdateEvent(level_update)
                self._dispatch(None, f"level-update/{t_frame}", level_update_evt)
                self.create_rooms(level_update)

                for t_msg, msg in self._server.receiver.receive(until=t_frame):
                    self.handle(t_msg, msg)

                for entity in self.entities.values():
                    entity.tick(dt_frame, t_frame)

                for room in self._rooms:
                    room.tick()

                # TODO: create/delete_entitiy into loop function using a TickCtx
                for entity in self._created_entities:
                    self._create_entity(entity)
                for entity in self._deleted_entities:
                    self._delete_entity(entity)
                del self._created_entities
                del self._deleted_entities

            # send events to clients
            for client in self._clients.values():
                for evt in client.events.collect():
                    game_evt = ServerGameEvent(client.last_ack, evt)
                    self._server.network.send(client.ip, game_evt)

            # cleanup udpate
            last_t = t_update
            clock.tick(1 / NetworkConstants.SERVER_TIMESTEP)


class Server(Stoppable):
    _logger = logging.getLogger(f"{__name__}.Server")
    network: Network[EventType]
    ip: IpV4
    receiver: Receiver[EventType]
    stopped: Atom[bool]

    def __init__(self, network: Network[EventType], ip: IpV4) -> None:
        self.network = network
        self.ip = ip
        self.receiver = Receiver(network, self.ip)
        self.stopped = Atom(False)

    def loop(self) -> None:
        clients = LobbyState(self).loop()
        self._logger.info("stopped lobby")
        if isinstance(clients, Stopped):
            return
        self._logger.info("starting game")
        GameState(self, clients).loop()
        self._logger.info("stopped game")

    def stop(self) -> None:
        self.stopped.set(True)
