from dataclasses import dataclass
from collections.abc import Iterable
import pygame
from pygame import Vector2

from shared.time import Time
from shared.network import IpV4

type Acknoledgement = int
INITIAL_ACKNOLEDGEMENT: Acknoledgement = -1
type EntityId = int
type ClientId = int

type Position = Vector2
type Orientation = Vector2
type Motion = tuple[Position, Orientation]
type Color = pygame.Color


"""Communication protocol
"""

type ServerGameEventType = (ServerSpawnRobotEvent | ServerEntityEvent)
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
    action: bool


# Server to client events


@dataclass(frozen=True)
class ServerConnectionConfirmEvent:
    client_id: ClientId


@dataclass(frozen=True)
class ServerGameStartEvent:
    client_entity: EntityId
    entities: Iterable["ServerSpawnRobotEvent"]


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
