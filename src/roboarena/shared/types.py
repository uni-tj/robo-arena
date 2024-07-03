from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from roboarena.shared.network import IpV4
from roboarena.shared.time import Time
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import Level, LevelUpdate
    from roboarena.shared.entity import Entity

type Acknoledgement = int
INITIAL_ACKNOLEDGEMENT: Acknoledgement = -1
type EntityId = int
type ClientId = int

type Position = Vector[float]
type Orientation = Vector[float]
type Motion = tuple[Position, Orientation]
type Color = pygame.Color

type Entities = dict[EntityId, "Entity"]


"""Communication protocol
"""

type ServerGameEventType = (
    ServerSpawnRobotEvent
    | ServerSpawnPlayerBulletEvent
    | ServerDeleteEntityEvent
    | ServerEntityEvent
    | ServerLevelUpdateEvent
)
type ServerSpawnEventType = (ServerSpawnRobotEvent | ServerSpawnPlayerBulletEvent)
type ServerEventType = (
    ServerConnectionConfirmEvent
    | ServerGameStartEvent
    | ServerGameEvent[ServerGameEventType]
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


@dataclass(frozen=True)
class ServerLevelUpdateEvent:
    update: "LevelUpdate"


@dataclass(frozen=True)
class ServerSpawnPlayerBulletEvent:
    id: EntityId
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
