import functools
import logging
from typing import Any

import pygame
from pygame import RESIZABLE, Surface, event
from pygame.font import Font
from pygame.time import Clock

from roboarena.client.entity import (
    ClientEnemyRobot,
    ClientEntityType,
    ClientInputHandler,
    ClientPlayerRobot,
)
from roboarena.shared.constants import CLIENT_TIMESTEP, SERVER_IP
from roboarena.shared.custom_threading import Atom
from roboarena.shared.game import GameState as SharedGameState
from roboarena.shared.network import Arrived, IpV4, Network, Receiver
from roboarena.shared.rendering.renderer import Renderer
from roboarena.shared.time import Time, get_time
from roboarena.shared.types import (
    INITIAL_ACKNOLEDGEMENT,
    Acknoledgement,
    ClientConnectionRequestEvent,
    ClientGameEvent,
    ClientGameEventType,
    ClientId,
    ClientInputEvent,
    ClientLobbyReadyEvent,
    EntityId,
    EventType,
    Input,
    ServerConnectionConfirmEvent,
    ServerEntityEvent,
    ServerExtendLevelEvent,
    ServerGameEvent,
    ServerGameStartEvent,
    ServerSpawnRobotEvent,
)
from roboarena.shared.util import Counter, EventTarget, Stoppable, Stopped, counter
from roboarena.shared.utils.vector import Vector


def unexpected_evt(expected: str, actual: Any) -> str:
    return f"Unexpected event. Expected {expected}, got {actual}"


class QuitEvent:
    pass


@functools.lru_cache(typed=True)
def setup_font() -> Font:
    pygame.font.init
    default_font = pygame.font.get_default_font()
    return pygame.font.SysFont(default_font, 48)


class MenuState:
    _logger = logging.getLogger(f"{__name__}.MenuState")
    _client: "Client"
    _screen: Surface
    _font: Font

    def __init__(self, client: "Client", screen: Surface) -> None:
        self._client = client
        self._screen = screen
        self._font = setup_font()

    def render(self):
        self._screen.fill("black")
        text = self._font.render("Main Menu. Press wasd to start.", True, "white")
        self._screen.blit(text, (0, 0))
        pygame.display.flip()

    def loop(self) -> None:
        self._logger.debug("Entered loop")
        clock = Clock()
        while True:
            keys = pygame.key.get_pressed()
            if (
                keys[pygame.K_RIGHT]
                or keys[pygame.K_DOWN]
                or keys[pygame.K_LEFT]
                or keys[pygame.K_UP]
            ):
                break

            pygame.event.pump()
            self.render()
            # self._logger.debug("Rendered")
            clock.tick(1 / CLIENT_TIMESTEP)


class GameOverState:
    _logger = logging.getLogger(f"{__name__}.GameOverState")
    _client: "Client"
    _screen: Surface
    _font: Font

    def __init__(self, client: "Client", screen: Surface) -> None:
        self._client = client
        self._screen = screen
        self._font = setup_font()

    def render(self):
        self._screen.fill("black")
        text = self._font.render("Game over. Press wasd to continue.", True, "white")
        self._screen.blit(text, (0, 0))
        pygame.display.flip()

    def loop(self) -> Stopped | None:
        self._logger.debug("Entered loop")
        clock = Clock()
        while True:
            if self._client.stopped.get():
                return Stopped()
            keys = pygame.key.get_pressed()
            if (
                keys[pygame.K_RIGHT]
                or keys[pygame.K_DOWN]
                or keys[pygame.K_LEFT]
                or keys[pygame.K_UP]
            ):
                break

            pygame.event.pump()
            self.render()
            # self._logger.debug("Rendered")
            clock.tick(1 / CLIENT_TIMESTEP)


class GameState(SharedGameState):
    _logger = logging.getLogger(f"{__name__}.GameState")
    _client: "Client"
    _screen: Surface
    _renderer: Renderer
    _ack: Counter
    _client_id: ClientId
    _entity_id: EntityId
    _entity: ClientInputHandler
    entities: dict[EntityId, ClientEntityType]
    events: EventTarget[QuitEvent]

    def __init__(
        self,
        client: "Client",
        screen: Surface,
        client_id: ClientId,
        t_start: Time,
        start: ServerGameStartEvent,
    ) -> None:
        self._client = client
        self._screen = screen
        self._renderer = Renderer(screen, self)
        self._ack = counter()
        self._client_id = client_id
        self._entity_id = start.client_entity
        self.entities = {}
        self.events = EventTarget()

        self._logger.debug(f"initialize with t_start: {t_start}, start: {start}")

        self.level = start.level

        for spawn in start.entities:
            if spawn.id != start.client_entity:
                self.handle(t_start, ServerGameEvent(INITIAL_ACKNOLEDGEMENT, spawn))
                continue
            # initialize client entity
            entity = ClientPlayerRobot(self, spawn.motion, spawn.color)
            self.entities[spawn.id] = entity
            self._entity = entity
            self._logger.debug(f"intialized client entity: {self._entity}")
        self._logger.debug(f"initialized all entities: {self.entities}")

    def handle(self, t_msg: Time, msg: EventType):
        if not isinstance(msg, ServerGameEvent):
            self._logger.error(f"Unexpected event: {msg}")
            raise ValueError(f"Unexpected event: {msg}")
        last_ack, event = msg.last_ack, msg.event

        match event:
            case ServerEntityEvent(id, name, payload):
                self.entities[id].on_server(name, payload, msg.last_ack, t_msg)
            case ServerSpawnRobotEvent(id, motion, color):
                entity = ClientEnemyRobot(self, motion, color, last_ack, t_msg)
                self.entities[id] = entity
            case ServerExtendLevelEvent(level_diff):
                self.level |= level_diff

    def dispatch(self, event: ClientGameEventType) -> Acknoledgement:
        ack = next(self._ack)
        self._client.dispatch(
            ClientGameEvent(self._client_id, ack, event),
        )
        return ack

    def get_input(self):
        keys = pygame.key.get_pressed()
        (mouse_1, _, mouse_3) = pygame.mouse.get_pressed()
        mouse_pos_px = Vector.from_tuple(pygame.mouse.get_pos())
        mouse_pos_gu = self._renderer.screen2gu(mouse_pos_px, self._entity.position)
        # self._logger.debug(f"mouse_pos_gu: {mouse_pos_gu}")
        return Input(
            move_right=keys[pygame.K_RIGHT],
            move_down=keys[pygame.K_DOWN],
            move_left=keys[pygame.K_LEFT],
            move_up=keys[pygame.K_UP],
            primary=mouse_1,
            secondary=mouse_3,
            mouse=mouse_pos_gu,
        )

    def loop(self) -> Stopped:
        self._logger.debug("Enterered loop")
        last_t = get_time()
        clock = Clock()

        while True:
            if self._client.stopped.get():
                return Stopped()

            # init frame
            t = get_time()
            dt = t - last_t

            for t_msg, msg in self._client.receiver.receive():
                self.handle(t_msg, msg)

            input = self.get_input()
            ack = self.dispatch(ClientInputEvent(input, dt))
            self._entity.on_input(input, dt, ack)

            for _, entity in self.entities.items():
                entity.tick(dt, t)

            # pygame event handling
            for e in event.get():
                match e.type:
                    case pygame.QUIT:
                        self.events.dispatch(QuitEvent())
                    case _:
                        continue

            # rendering
            self._renderer.render(camera_position=self._entity.position)
            # self._logger.debug("Rendered")

            # cleanup frame
            last_t = t
            clock.tick(1 / CLIENT_TIMESTEP)


class Client(Stoppable):
    _logger = logging.getLogger(f"{__name__}/Client")
    ip: IpV4
    network: Network[EventType]
    receiver: Receiver[EventType]
    stopped: Atom[bool]
    events: EventTarget[QuitEvent]

    def __init__(self, network: Network[EventType], ip: IpV4):
        self.ip = ip
        self.network = network
        self.receiver = Receiver(network, ip)
        self.stopped = Atom(False)
        self.events = EventTarget()

    def dispatch(self, event: EventType) -> None:
        self.network.send(SERVER_IP, event)

    def loop(self) -> Stopped:
        pygame.init()
        screen = pygame.display.set_mode((1000, 1000), flags=RESIZABLE)

        menu_result = MenuState(self, screen).loop()
        if isinstance(menu_result, Stopped):
            return Stopped()

        self.dispatch(ClientConnectionRequestEvent(self.ip))
        # wait for connection confirmation
        client_id: None | ClientId = None
        while client_id is None:
            if self.stopped.get():
                return Stopped()
            arrived = self.network.receive_one(self.ip)
            if arrived is None:
                continue
            _, msg = arrived
            if not isinstance(msg, ServerConnectionConfirmEvent):
                self._logger.critical(
                    unexpected_evt("ServerConnectionConfirmEvent", msg)
                )
                raise ValueError(unexpected_evt("ServerConnectionConfirmEvent", msg))
            # handle connection confirm
            client_id = msg.client_id
        self._logger.info("Conntected to server")

        self.dispatch(ClientLobbyReadyEvent(client_id))
        # wait for game start
        start: None | Arrived[ServerGameStartEvent] = None
        while start is None:
            if self.stopped.get():
                return Stopped()
            arrived = self.network.receive_one(self.ip)
            if arrived is None:
                continue
            t_msg, msg = arrived
            if not isinstance(msg, ServerGameStartEvent):
                self._logger.critical(
                    unexpected_evt("ServerConnectionConfirmEvent", msg)
                )
                raise ValueError(unexpected_evt("ServerConnectionConfirmEvent", msg))
            start = t_msg, msg
        self._logger.info("Started game")

        game_state = GameState(self, screen, client_id, start[0], start[1])
        game_state.events.add_listener(QuitEvent, self.events.dispatch)
        return game_state.loop()

    def stop(self) -> None:
        return self.stopped.set(True)
