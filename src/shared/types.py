from dataclasses import dataclass
from collections.abc import Iterable
import pygame
from pygame import Vector2

from shared.time import Time
from shared.network import IpV4

type Acknoledgement = int
type EntityId = int
type ClientId = int

type Position = Vector2
type Orientation = Vector2
type Motion = tuple[Position, Orientation]
type Color = pygame.Color


"""Communication protocol
"""

type ServerSubEventType = (
    ServerConnectionConfirmEvent | ServerSpawnRobotEvent | ServerEntityEvent
)
type ServerEventType = ServerEvent[ServerSubEventType]
type ClientSubEventType = ClientConnectionRequestEvent | ClientInputEvent
type ClientEventType = ClientEvent[ClientSubEventType]
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
class ServerEvent[Evt]:
    last_ack: Acknoledgement
    event: Evt


@dataclass(frozen=True)
class ServerConnectionConfirmEvent:
    client_id: ClientId
    client_entity: EntityId
    world: Iterable[ServerSubEventType]


@dataclass(frozen=True)
class ServerEntityEvent:
    entity: EntityId
    type: str
    payload: object


@dataclass(frozen=True)
class ServerSpawnRobotEvent:
    entity: EntityId
    motion: Motion
    color: Color


# Client to server events


""" Set ClientEvent.client to this value when sending ConnectionRequest

It will be ignored and the assigned id is send as ConnectionConfirm.client_id
"""
INITIAL_CLIENT_ID = -1


@dataclass(frozen=True)
class ClientEvent[Evt]:
    ack: Acknoledgement
    client: ClientId
    event: Evt


@dataclass(frozen=True)
class ClientConnectionRequestEvent:
    ip: IpV4


@dataclass(frozen=True)
class ClientInputEvent:
    input: Input
    dt: Time
