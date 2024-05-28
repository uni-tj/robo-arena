from collections.abc import Iterable, Sequence
import pygame
from pygame.time import Clock

from shared.constants import CLIENT_TIMESTEP, SERVER_IP
from shared.time import get_time
from shared.util import counter
from shared.types import (
    INITIAL_CLIENT_ID,
    Acknoledgement,
    ClientEvent,
    ClientId,
    ClientInputEvent,
    ClientSubEventType,
    EntityId,
    Input,
    ClientConnectionRequestEvent,
    ServerConnectionConfirmEvent,
    ServerEntityEvent,
    ServerEvent,
    EventType,
    ServerSpawnRobotEvent,
)
from shared.network import Arrived, IpV4, Network
from client.entity import (
    ClientEnemyRobot,
    ClientPlayerRobot,
    ClientInputHandler,
    ClientEntityType,
)


class Client:
    ack = counter()
    ip: IpV4
    network: Network[EventType]
    id: ClientId = INITIAL_CLIENT_ID
    entity_id: EntityId
    entity: ClientInputHandler

    entities: dict[EntityId, ClientEntityType] = {}

    def __init__(self, network: Network[EventType], ip: IpV4):
        # init values
        self.ip = ip
        self.network = network
        # connect to server
        self.dispatch(ClientConnectionRequestEvent(self.ip))
        # wait for connection confirmation
        while True:
            messages = self.fetch_events()
            if len(messages) == 0:
                continue
            (t_msg, msg), *other_messages = messages
            if not isinstance(msg, ServerEvent):
                raise ValueError("client: message not ServerEvent")
            if not isinstance(msg.event, ServerConnectionConfirmEvent):
                raise ValueError("client: event not ConnectionEvent")
            # handle connection confirm
            self.last_ack = msg.last_ack
            self.id = msg.event.client_id
            self.entity_id = msg.event.client_entity
            self.handle_events(
                map(lambda _: (t_msg, ServerEvent(msg.last_ack, _)), msg.event.world)
            )
            # handle other messages
            self.handle_events(other_messages)
            break

        # run main loop
        self.loop()

    def handle_events(self, messages: Iterable[Arrived[EventType]]):
        for t_msg, msg in messages:
            if not isinstance(msg, ServerEvent):
                raise ValueError("handle_messages: not ServerEvent")
            match msg.event:
                case ServerEntityEvent(id, name, payload):
                    self.entities[id].on_server(name, payload, msg.last_ack, t_msg)
                case ServerSpawnRobotEvent(id, motion, color):
                    entity: ClientEntityType
                    if id == self.entity_id:
                        _entity = ClientPlayerRobot(motion, color)
                        self.entity = _entity
                        entity = _entity
                    else:
                        entity = ClientEnemyRobot(motion, color, msg.last_ack, t_msg)
                    self.entities[id] = entity
                case ServerConnectionConfirmEvent():
                    raise ValueError("client: unexpected connection confirm")

    def dispatch(self, event: ClientSubEventType) -> Acknoledgement:
        ack = next(self.ack)
        self.network.send(
            SERVER_IP,
            ClientEvent(ack, self.id, event),
        )
        return ack

    def fetch_events(self) -> Sequence[Arrived[EventType]]:
        return self.network.receive(self.ip)

    def get_input(self):
        keys = pygame.key.get_pressed()
        return Input(
            move_right=keys[pygame.K_RIGHT],
            move_down=keys[pygame.K_DOWN],
            move_left=keys[pygame.K_LEFT],
            move_up=keys[pygame.K_UP],
            action=keys[pygame.K_a],
        )

    def loop(self):
        last_t = get_time()
        clock = Clock()

        pygame.init()
        screen = pygame.display.set_mode((1000, 1000))
        while True:
            # init frame
            t = get_time()
            dt = t - last_t

            self.handle_events(self.fetch_events())

            input = self.get_input()
            ack = self.dispatch(ClientInputEvent(input, dt))
            self.entity.on_input(input, dt, ack)

            for _, entity in self.entities.items():
                entity.tick(dt, t)

            # rendering
            pygame.event.pump()
            screen.fill("black")
            for entity in self.entities.values():
                entity.render(screen)
            pygame.display.flip()
            print("rendered")

            # cleanup frame
            last_t = t
            clock.tick(1 / CLIENT_TIMESTEP)
