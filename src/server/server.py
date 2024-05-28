from dataclasses import dataclass
from typing import Optional
from collections.abc import Sequence, Iterable
from pygame import Vector2, Color
from pygame.time import Clock

from shared.network import IpV4, Network, Receiver, Arrived
from shared.time import get_time
from shared.types import (
    Acknoledgement,
    ClientId,
    EntityId,
    ServerSubEventType,
    ServerEntityEvent,
    EventType,
    ClientEvent,
    ClientConnectionRequestEvent,
    ServerConnectionConfirmEvent,
    ServerSpawnRobotEvent,
    ClientInputEvent,
    ServerEvent,
)
from shared.util import gen_id
from shared.constants import SERVER_TIMESTEP, SERVER_FRAMES_PER_TIMESTEP
from server.events import EventBuffer, EventName, Dispatch
from server.entity import (
    ServerInputHandler,
    ServerEntityType,
    ServerPlayerRobot,
    ServerEnemyRobot,
)


@dataclass
class ClientInfo:
    ip: IpV4
    last_ack: Acknoledgement
    entity: ServerInputHandler
    events: EventBuffer[ServerSubEventType] = EventBuffer()


class Server:
    clients: dict[ClientId, ClientInfo] = {}
    ip: IpV4
    network: Network[EventType]
    receiver: Receiver[EventType]

    entities: dict[EntityId, ServerEntityType]

    def __init__(self, network: Network[EventType], ip: IpV4) -> None:
        self.ip = ip
        self.network = network
        self.receiver = Receiver(network, self.ip)

        enemy_id = 0
        enemy = ServerEnemyRobot(
            (Vector2(10, 1), Vector2(1, 0)),
            Color(255, 0, 0),
            self.dispatch_factory(None, enemy_id),
        )
        self.entities = {enemy_id: enemy}

        self.loop()

    def dispatch_factory(
        self, client: Optional[ClientId], entity: EntityId
    ) -> Dispatch[object]:
        SEE = ServerEntityEvent
        return lambda n, e: self.dispatch(client, f"{entity}/{n}", SEE(entity, n, e))

    def dispatch(
        self,
        client: Optional[ClientId],
        event_name: EventName,
        event: ServerSubEventType,
    ):
        targets_ids = [client] if client is not None else self.clients.keys()
        for target_id in targets_ids:
            target = self.clients[target_id]
            target.events.dispatch(event_name, event)

    def handle_messages(self, messages: Sequence[Arrived[EventType]]) -> None:
        for _, msg in messages:
            if not isinstance(msg, ClientEvent):
                raise ValueError("handle_messages: not ClientEvent")
            if isinstance(msg.event, ClientConnectionRequestEvent):
                client_id = gen_id(self.clients.keys())
                entity_id, entity = self.gen_client_entity(client_id)
                self.entities[entity_id] = entity
                client = ClientInfo(msg.event.ip, msg.ack, entity)
                self.clients[client_id] = client
                self.dispatch(
                    client_id,
                    f"ConnectionConfirm/{client_id}",
                    ServerConnectionConfirmEvent(
                        client_id, entity_id, self.world_as_messages()
                    ),
                )
                continue

            self.clients[msg.client].last_ack = msg.ack
            match msg.event:
                case ClientInputEvent(input, dt):
                    self.clients[msg.client].entity.on_input(input, dt)

    def gen_client_entity(self, id: EntityId) -> tuple[EntityId, ServerPlayerRobot]:
        entity_id = gen_id(self.entities.keys())
        entity = ServerPlayerRobot(
            (Vector2(10, 5), Vector2(1, 0)),
            Color(0, 255, 0),
            self.dispatch_factory(None, entity_id),
        )
        return (entity_id, entity)

    def world_as_messages(self) -> Iterable[ServerSubEventType]:

        def entity_as_event(
            entity_id: EntityId, entity: ServerEntityType
        ) -> ServerSubEventType:
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

        return map(lambda _: entity_as_event(_[0], _[1]), self.entities.items())

    def loop(self) -> None:
        last_t = get_time()
        clock = Clock()

        # pygame.init()
        # screen = pygame.display.set_mode((1000, 1000))
        while True:
            # init update
            t_update = get_time()
            dt_update = t_update - last_t
            dt_frame = dt_update / SERVER_FRAMES_PER_TIMESTEP

            # Each update is split into 3 frames to get more precise results
            for i in range(SERVER_FRAMES_PER_TIMESTEP):
                t_frame = last_t + i * dt_frame

                self.handle_messages(self.receiver.received_until(t_frame))

                for entity in self.entities.values():
                    entity.tick(dt_frame, t_frame)

            # send events to clients
            for client in self.clients.values():
                for evt in client.events.collect():
                    self.network.send(client.ip, ServerEvent(client.last_ack, evt))

            # cleanup udpate
            last_t = t_update
            clock.tick(1 / SERVER_TIMESTEP)
