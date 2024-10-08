from collections.abc import Collection, Iterable
from dataclasses import dataclass
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    NoReturn,
    Sequence,
    SupportsIndex,
)

import pygame

from roboarena.shared.constants import WeaponConstants
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.entity import (
        ClientBullet,
        ClientDoorEntity,
        ClientEnemyRobot,
        ClientPlayerRobot,
    )
    from roboarena.server.entity import (
        ServerBullet,
        ServerDoorEntity,
        ServerEnemyRobot,
        ServerPlayerRobot,
    )
    from roboarena.server.level_generation.level_generator import Tileset
    from roboarena.shared.block import Block
    from roboarena.shared.entity import Entity


type Acknoledgement = int
type EntityId = int
type ClientId = int

type IpV4 = int
"""Time of arrival and message, internal type"""
type Packet[Message] = tuple[Time, Message]
"""Time of arrival and message"""
type Arrived[Message] = tuple[Time, Message]

type Time = float
"""In seconds"""

type Counter = Generator[int, Any, NoReturn]

type TupleVector = tuple[int, int]

type ShapeLike = SupportsIndex | Sequence[SupportsIndex]
"""Pygame"""

type Tile = int
"""Square of 25x25 blocks generated as one unit by the wafe function collapse"""
type TilePosition = Vector[int]
type PossibleTiles = int
type WFCMap = dict[TilePosition, PossibleTiles]
type WFCUpdate = Iterable[tuple[TilePosition, int]]
type Ts = "Tileset"

type BlockPosition = Vector[int]
type Level = dict[BlockPosition, "Block"]
type LevelUpdate = Iterable[tuple[BlockPosition, "Block"]]

type Position = Vector[float]
type Velocity = Vector[float]
type Motion = tuple[Position, Velocity]
type Color = pygame.Color

type PlayerPosition = Vector[float]

type Entities = dict[EntityId, "Entity"]

type Path = str

type ClientEntityType = (
    "ClientPlayerRobot | ClientEnemyRobot | ClientBullet | ClientDoorEntity"
)
type ServerEntityType = (
    "ServerPlayerRobot | ServerEnemyRobot | ServerBullet | ServerDoorEntity"
)

type BulletMoveCtx = tuple[Time]
type PlayerRobotMoveCtx = tuple[Input, Time]
type EnemyRobotMoveCtx = tuple[Time]

type EventName = str
type Dispatch[Evt] = Callable[[EventName, Evt], None]
type SimpleDispatch[Evt] = Callable[[Evt], None]


@dataclass(frozen=True)
class PygameColor:
    r: int
    g: int
    b: int
    alpha: int = 255

    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.alpha)

    @staticmethod
    def light_grey() -> "PygameColor":
        return PygameColor(211, 211, 211)

    @staticmethod
    def grey() -> "PygameColor":
        return PygameColor(128, 128, 128)

    @staticmethod
    def red() -> "PygameColor":
        return PygameColor(255, 0, 0)

    @staticmethod
    def green() -> "PygameColor":
        return PygameColor(0, 255, 0)

    @staticmethod
    def blue() -> "PygameColor":
        return PygameColor(0, 0, 255)


@dataclass(frozen=True)
class StartFrameEvent:
    """Fired when a new frame begins."""


@dataclass(frozen=True)
class QuitEvent:
    """Fired when then user requests to quit the program"""


@dataclass(frozen=True)
class ChangedEvent[T]:
    """Fired after a value changed"""

    old: T
    new: T


@dataclass(frozen=True)
class HitEvent:
    """Fired after entity was hit"""


@dataclass(frozen=True)
class DeathEvent:
    """Fired when entity dies"""


@dataclass(frozen=True)
class CloseEvent:
    """Fired when the doors of an room close"""


@dataclass(frozen=True)
class OpenEvent:
    """Fired when the doors of an room open"""


@dataclass(frozen=True)
class ShotEvent:
    """Fired after shooting"""


@dataclass(frozen=True)
class Weapon:
    weapon_speed: float
    """In shots per second"""
    bullet_speed: float
    """In gu per second"""
    bullet_strength: int

    @cached_property
    def wepaon_cooldown(self):
        return 1 / self.weapon_speed


basic_weapon = Weapon(
    weapon_speed=WeaponConstants.WEAPON_SPEED,
    bullet_speed=WeaponConstants.BULLET_SPEED,
    bullet_strength=WeaponConstants.BULLET_Strength,
)


"""Communication protocol
"""

type ServerGameEventType = (
    ServerSpawnRobotEvent
    | ServerSpawnBulletEvent
    | ServerSpawnDoorEvent
    | ServerDeleteEntityEvent
    | ServerEntityEvent
    | ServerLevelUpdateEvent
    | ServerMarkerEvent
    | ServerMarkVectEvent
)
type ServerSpawnEventType = (
    ServerSpawnRobotEvent | ServerSpawnDoorEvent | ServerSpawnBulletEvent
)
type ServerEventType = (
    ServerConnectionConfirmEvent
    | ServerGameStartEvent
    | ServerGameEvent[ServerGameEventType]
    | ServerGameEndEvent
)
type ClientGameEventType = ClientInputEvent
type ClientEventType = (
    ClientConnectionRequestEvent
    | ClientLobbyReadyEvent
    | ClientGameEvent[ClientInputEvent]
)
type EventType = ServerEventType | ClientEventType


@dataclass(frozen=True)
class Input:
    dt: Time

    move_right: bool
    move_down: bool
    move_left: bool
    move_up: bool

    primary: bool
    secondary: bool
    mouse: Position


# Server to client events


@dataclass(frozen=True)
class ServerConnectionConfirmEvent:
    client_id: ClientId


@dataclass(frozen=True)
class ServerGameStartEvent:
    client_entity: EntityId
    entities: Iterable[ServerSpawnEventType]
    level: "Level"


@dataclass(frozen=True)
class ServerGameEvent[Evt]:
    last_ack: Acknoledgement
    event: Evt


@dataclass(frozen=True)
class ServerGameEndEvent:
    pass


@dataclass(frozen=True)
class ServerEntityEvent:
    entity: EntityId
    type: str
    payload: object


@dataclass(frozen=True)
class ServerSpawnRobotEvent:
    id: EntityId
    health: int
    motion: Motion
    color: Color
    weapon: Weapon


@dataclass(frozen=True)
class ServerSpawnDoorEvent:
    id: EntityId
    position: Position
    open: bool


@dataclass(frozen=True)
class ServerLevelUpdateEvent:
    update: "LevelUpdate"


@dataclass(frozen=True)
class Marker:
    position: Vector[float]
    color: PygameColor


@dataclass(frozen=True)
class MarkerVect:
    start: Vector[float]
    end: Vector[float]
    color: PygameColor


@dataclass(frozen=True)
class ServerMarkerEvent:
    markers: Collection[Marker]


@dataclass(frozen=True)
class ServerMarkVectEvent:
    markers: Collection[MarkerVect]


@dataclass(frozen=True)
class ServerSpawnBulletEvent:
    id: EntityId
    friendly: bool
    position: Vector[float]
    velocity: Vector[float]


@dataclass(frozen=True)
class ServerDeleteEntityEvent:
    id: EntityId


# Client to server events


@dataclass(frozen=True)
class ClientConnectionRequestEvent:
    ip: IpV4


@dataclass(frozen=True)
class ClientLobbyReadyEvent:
    client_id: ClientId


@dataclass(frozen=True)
class ClientGameEvent[Evt]:
    client_id: ClientId
    ack: Acknoledgement
    event: Evt


@dataclass(frozen=True)
class ClientInputEvent:
    input: Input
    dt: Time
