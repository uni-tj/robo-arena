from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import pygame

from roboarena.server.level_generation.tile import Tile
from roboarena.shared.network import IpV4
from roboarena.shared.time import Time
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.block import Block
    from roboarena.shared.entity import Entity

type Acknoledgement = int
INITIAL_ACKNOLEDGEMENT: Acknoledgement = -1
type EntityId = int
type ClientId = int

type Position = Vector[float]
type Orientation = Vector[float]
type Motion = tuple[Position, Orientation]
type Color = pygame.Color

type TileMap = dict[Vector[int], Optional[Tile]]
type Level = dict[Vector[int], "Block"]

type Entities = dict[EntityId, "Entity"]


"""Communication protocol
"""

type ServerGameEventType = (
    ServerSpawnRobotEvent | ServerEntityEvent | ServerExtendLevelEvent
)
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
    entities: Iterable["ServerSpawnRobotEvent"]
    level: Level


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
    motion: Motion
    color: Color


@dataclass(frozen=True)
class ServerExtendLevelEvent:
    level_diff: Level


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
