import functools
import logging
from collections import deque
from typing import TYPE_CHECKING, Any

import pygame
from attrs import define
from pygame import RESIZABLE, Surface, event
from pygame.font import Font
from pygame.time import Clock

from roboarena.client.ambience_sound import AmbienceSound
from roboarena.client.entity import (
    ClientDoorEntity,
    ClientEnemyRobot,
    ClientEntityType,
    ClientInputHandler,
    ClientPlayerBullet,
    ClientPlayerRobot,
)
from roboarena.client.keys import load_keys
from roboarena.client.master_mixer import MUSIC_DONE, MasterMixer
from roboarena.client.menu.main_menu import MainMenu
from roboarena.shared.constants import CLIENT_TIMESTEP, SERVER_IP
from roboarena.shared.custom_threading import Atom
from roboarena.shared.game import GameState as SharedGameState
from roboarena.shared.game_ui import GameUI
from roboarena.shared.network import Arrived, IpV4, Network, Receiver
from roboarena.shared.rendering.renderer import GameRenderer
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
    Marker,
    QuitEvent,
    ServerConnectionConfirmEvent,
    ServerDeleteEntityEvent,
    ServerEntityEvent,
    ServerGameEvent,
    ServerGameStartEvent,
    ServerLevelUpdateEvent,
    ServerMarkerEvent,
    ServerSpawnDoorEvent,
    ServerSpawnPlayerBulletEvent,
    ServerSpawnRobotEvent,
    StartFrameEvent,
)
from roboarena.shared.util import Counter, EventTarget, Stoppable, Stopped, counter
from roboarena.shared.utils.vector import Vector
from roboarena.shared.weapon import LaserGun

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import Level


def unexpected_evt(expected: str, actual: Any) -> str:
    return f"Unexpected event. Expected {expected}, got {actual}"


@functools.lru_cache(typed=True)
def setup_font() -> Font:
    pygame.font.init
    default_font = pygame.font.get_default_font()
    return pygame.font.SysFont(default_font, 48)


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


@define
class CameraPosition:
    _camera_pos: Vector[float]
    _RESPONSIVENESS_FACTOR: float = 0.025
    """Regulates the responsiveness. [0.01, 0.05] works with reasonable speeds"""

    def get(self) -> Vector[float]:
        return self._camera_pos

    def update(self, player_pos: Vector[float]) -> Vector[float]:
        self._camera_pos += (
            player_pos - self._camera_pos
        ) * self._RESPONSIVENESS_FACTOR

        return self._camera_pos


class GameState(SharedGameState):
    _logger = logging.getLogger(f"{__name__}.GameState")
    _client: "Client"
    _screen: Surface
    _renderer: GameRenderer
    _master_mixer: MasterMixer
    _ambience_sound: AmbienceSound
    _ack: Counter
    _client_id: ClientId
    _entity_id: EntityId
    _entity: ClientInputHandler
    env = "client"
    entities: dict[EntityId, ClientEntityType]
    markers: deque[Marker]
    level: "Level"
    _camera_pos: CameraPosition

    def __init__(
        self,
        client: "Client",
        screen: Surface,
        client_id: ClientId,
        t_start: Time,
        start: ServerGameStartEvent,
        master_mixer: MasterMixer,
    ) -> None:
        self._client = client
        self._screen = screen
        self._renderer = GameRenderer(screen, self)
        self._master_mixer = master_mixer
        self.game_ui = GameUI(LaserGun())
        self._ack = counter()
        self._client_id = client_id
        self._entity_id = start.client_entity
        self.entities = {}  # type: ignore
        self.events = EventTarget()
        self.markers = deque(maxlen=1000)

        self._logger.debug(f"initialize with t_start: {t_start}, start: {start}")

        self.level = start.level

        for spawn in start.entities:
            if spawn.id != start.client_entity:
                self.handle(t_start, ServerGameEvent(INITIAL_ACKNOLEDGEMENT, spawn))
                continue
            # initialize client entity
            if not isinstance(spawn, ServerSpawnRobotEvent):
                self._logger.critical("client entity no robot")
                raise Exception("client entity no robot")
            entity = ClientPlayerRobot(
                self, spawn.health, spawn.motion, spawn.color, spawn.weapon
            )
            self.entities[spawn.id] = entity
            self._entity = entity
            self._logger.debug(f"intialized client entity: {self._entity}")
        self._logger.debug(f"initialized all entities: {self.entities}")

        self.set_keys()

        self._camera_pos = CameraPosition(self._entity.position)

    def handle(self, t_msg: Time, msg: EventType):
        if not isinstance(msg, ServerGameEvent):
            self._logger.error(f"Unexpected event: {msg}")
            raise ValueError(f"Unexpected event: {msg}")
        last_ack, event = msg.last_ack, msg.event

        match event:
            case ServerEntityEvent(id, name, payload):
                self.entities[id].on_server(name, payload, msg.last_ack, t_msg)
            case ServerSpawnRobotEvent(id, health, motion, color, weapon):
                entity = ClientEnemyRobot(
                    self, health, motion, color, weapon, last_ack, t_msg
                )
                self.entities[id] = entity
            case ServerSpawnDoorEvent(id, position, open):
                entity = ClientDoorEntity(self, position, open)
                self.entities[id] = entity
            case ServerSpawnPlayerBulletEvent(id, position, velocity):
                entity = ClientPlayerBullet(
                    self, position, velocity, msg.last_ack, t_msg
                )
                self.entities[id] = entity
            case ServerDeleteEntityEvent(id):
                del self.entities[id]
            case ServerLevelUpdateEvent(update):
                self.level |= update
            case ServerMarkerEvent(markers):
                self.markers += markers

    def dispatch(self, event: ClientGameEventType) -> Acknoledgement:
        ack = next(self._ack)
        self._client.dispatch(
            ClientGameEvent(self._client_id, ack, event),
        )
        return ack

    def set_keys(self) -> None:
        self._keys = load_keys()

    def get_input(self, dt: Time):
        keys = pygame.key.get_pressed()
        (mouse_1, _, mouse_3) = pygame.mouse.get_pressed()
        mouse_pos_px = Vector.from_tuple(pygame.mouse.get_pos())
        mouse_pos_gu = self._renderer.screen2gu(mouse_pos_px, self._camera_pos.get())
        # self._logger.debug(f"mouse_pos_gu: {mouse_pos_gu}")
        return Input(
            dt=dt,
            move_right=keys[self._keys["key_right"]],
            move_down=keys[self._keys["key_down"]],
            move_left=keys[self._keys["key_left"]],
            move_up=keys[self._keys["key_up"]],
            primary=mouse_1,
            secondary=mouse_3,
            mouse=mouse_pos_gu,
        )

    def loop(self) -> Stopped:
        self._logger.debug("Enterered loop")
        last_t = get_time()
        clock = Clock()
        _ambience_sound = AmbienceSound(self._master_mixer)

        while True:
            if self._client.stopped.get():
                return Stopped()

            # init frame
            t = get_time()
            dt = t - last_t

            self.events.dispatch(StartFrameEvent())

            for t_msg, msg in self._client.receiver.receive():
                self.handle(t_msg, msg)

            input = self.get_input(dt)
            ack = self.dispatch(ClientInputEvent(input, dt))
            self._entity.on_input(input, dt, ack, t)

            for _, entity in self.entities.items():
                entity.tick(dt, t)

            # pygame event handling
            for e in event.get():
                if e.type == pygame.QUIT:
                    self.events.dispatch(QuitEvent())
                elif e.type == MUSIC_DONE:
                    _ambience_sound.switch_music()
                else:
                    continue

            # rendering
            camers_pos = self._camera_pos.update(self._entity.position)
            self._renderer.render(camera_position=camers_pos)
            # self._logger.debug("Rendered")

            # ambience sound
            _ambience_sound.tick()

            # cleanup frame
            last_t = t
            clock.tick(1 / CLIENT_TIMESTEP)

        self._ambience_sound.stop()


class Client(Stoppable):
    _logger = logging.getLogger(f"{__name__}/Client")
    ip: IpV4
    network: Network[EventType]
    receiver: Receiver[EventType]
    stopped: Atom[bool]
    events: EventTarget[QuitEvent]
    _master_mixer: MasterMixer

    def __init__(self, network: Network[EventType], ip: IpV4):
        self.ip = ip
        self.network = network
        self.receiver = Receiver(network, ip)
        self.stopped = Atom(False)
        self.events = EventTarget()
        self._master_mixer = MasterMixer()

    def dispatch(self, event: EventType) -> None:
        self.network.send(SERVER_IP, event)

    def loop(self) -> Stopped:
        pygame.init()
        screen = pygame.display.set_mode(
            (1000, 1000),
            flags=RESIZABLE,
            vsync=1,
        )

        menu = MainMenu(screen, self, self._master_mixer)
        menu.events.add_listener(QuitEvent, self.events.dispatch)
        if isinstance(menu.loop(), Stopped):
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

        game_state = GameState(
            self, screen, client_id, start[0], start[1], self._master_mixer
        )
        game_state.events.add_listener(QuitEvent, self.events.dispatch)
        return game_state.loop()

    def stop(self) -> None:
        return self.stopped.set(True)
