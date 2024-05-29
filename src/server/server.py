import logging
from dataclasses import dataclass
from typing import Optional

from pygame import Color, Vector2
from pygame.time import Clock

from server.entity import (
    ServerEnemyRobot,
    ServerEntityType,
    ServerInputHandler,
    ServerPlayerRobot,
)
from server.events import Dispatch, EventBuffer, EventName
from shared.constants import SERVER_FRAMES_PER_TIMESTEP, SERVER_TIMESTEP
from shared.game import GameState as SharedGameState
from shared.network import IpV4, Network, Receiver
from shared.time import Time, get_time
from shared.types import (
    INITIAL_ACKNOLEDGEMENT,
    Acknoledgement,
    ClientConnectionRequestEvent,
    ClientGameEvent,
    ClientId,
    ClientInputEvent,
    ClientLobbyReadyEvent,
    EntityId,
    EventType,
    ServerConnectionConfirmEvent,
    ServerEntityEvent,
    ServerGameEvent,
    ServerGameEventType,
    ServerGameStartEvent,
    ServerSpawnRobotEvent,
)
from shared.util import gen_id

logger = logging.getLogger(__name__)


class LobbyState:
    @dataclass
    class ClientInfo:
        ip: IpV4
        ready: bool

    _logger = logging.getLogger(f"{__name__}.LobbyState")
    _server: "Server"
    _clients: dict[ClientId, ClientInfo] = {}

    def __init__(self, server: "Server") -> None:
        self._server = server

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

    def loop(self) -> dict[EntityId, IpV4]:
        logger.debug("enter LobbyState.loop")
        while len(self._clients) == 0 or not all(
            _.ready for _ in self._clients.values()
        ):
            for t_msg, msg in self._server.receiver.received():
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
        events: EventBuffer[ServerGameEventType] = EventBuffer()

    _logger = logging.getLogger(f"{__name__}.GameState")
    _server: "Server"
    _clients: dict[ClientId, ClientInfo] = {}
    _entities: dict[EntityId, ServerEntityType] = {}

    def __init__(self, server: "Server", clients: dict[ClientId, IpV4]) -> None:
        self._server = server

        self._logger.debug(f"initialize with clients: {clients}")

        enemy_id = 0
        enemy = ServerEnemyRobot(
            (Vector2(10, 1), Vector2(1, 0)),
            Color(255, 0, 0),
            self.dispatch_factory(None, enemy_id),
        )
        self._entities[enemy_id] = enemy

        for client_id, ip in clients.items():
            entity_id, entity = self.gen_client_entity()
            self._clients[client_id] = GameState.ClientInfo(
                ip, INITIAL_ACKNOLEDGEMENT, entity_id, entity
            )
            self._entities[entity_id] = entity

        self._logger.debug(f"initialized entities: {self._entities}")

        def entity_as_event(
            entity_id: EntityId, entity: ServerEntityType
        ) -> ServerSpawnRobotEvent:
            match entity:
                case ServerPlayerRobot():
                    return ServerSpawnRobotEvent(
                        entity_id,
                        entity.motion.get(),
                        entity.color.get(),
                    )
                case ServerEnemyRobot():
                    return ServerSpawnRobotEvent(
                        entity_id,
                        entity.motion.get(),
                        entity.color.get(),
                    )

        spawn_events = [entity_as_event(i, e) for i, e in self._entities.items()]
        for client in self._clients.values():
            self._server.network.send(
                client.ip, ServerGameStartEvent(client.entity_id, spawn_events)
            )

    def dispatch_factory(
        self, client: Optional[ClientId], entity: EntityId
    ) -> Dispatch[object]:
        SEE = ServerEntityEvent
        return lambda n, e: self.dispatch(client, f"{entity}/{n}", SEE(entity, n, e))

    def dispatch(
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
                        self._clients[client_id].entity.on_input(input, dt)
            case _:
                self._logger.error(f"Unexpected event: {msg}")
                raise ValueError(f"Unexpected event: {msg}")

    def gen_client_entity(self) -> tuple[EntityId, ServerPlayerRobot]:
        entity_id = gen_id(self._entities.keys())
        entity = ServerPlayerRobot(
            (Vector2(10, 5), Vector2(1, 0)),
            Color(0, 255, 0),
            self.dispatch_factory(None, entity_id),
        )
        return (entity_id, entity)

    def loop(self) -> None:
        last_t = get_time()
        clock = Clock()

        while True:
            # init update
            t_update = get_time()
            dt_update = t_update - last_t
            dt_frame = dt_update / SERVER_FRAMES_PER_TIMESTEP

            # Each update is split into 3 frames to get more precise results
            for i in range(SERVER_FRAMES_PER_TIMESTEP):
                t_frame = last_t + i * dt_frame

                for t_msg, msg in self._server.receiver.received_until(t_frame):
                    self.handle(t_msg, msg)

                for entity in self._entities.values():
                    entity.tick(dt_frame, t_frame)

            # send events to clients
            for client in self._clients.values():
                for evt in client.events.collect():
                    game_evt = ServerGameEvent(client.last_ack, evt)
                    self._server.network.send(client.ip, game_evt)

            # cleanup udpate
            last_t = t_update
            clock.tick(1 / SERVER_TIMESTEP)


class Server:
    _logger = logging.getLogger(f"{__name__}.Server")
    network: Network[EventType]
    ip: IpV4
    receiver: Receiver[EventType]

    def __init__(self, network: Network[EventType], ip: IpV4) -> None:
        self.network = network
        self.ip = ip
        self.receiver = Receiver(network, self.ip)

    def loop(self) -> None:
        clients = LobbyState(self).loop()
        self._logger.info("closed lobby, starting game")
        GameState(self, clients).loop()
