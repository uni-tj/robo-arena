from abc import ABC, abstractmethod
from bisect import insort_right
from collections import deque
from collections.abc import Sequence, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from queue import Empty, Queue
from random import getrandbits
from threading import Lock
from time import perf_counter
from typing import (
    Any,
    Callable,
    Optional,
    TypedDict,
    NotRequired,
    TypeVar,
    Protocol,
    assert_never,
)
from functools import partial
from threading import Thread

import pygame
from pygame import Vector2, Vector3, Surface

type EntityId = int
type Entities = dict[EntityId, Entity]
type InputId = int
type ClientId = int
type Time = float

SERVER_TIMESTEP = 1 / 20
SERVER_FRAMES_PER_TIMESTEP = 3
CLIENT_FRAMERATE = 60
SERVER_IP = 0x00000000
PIXELS_PER_BLOCK = 20
# CLIENT_TIMESTEP = 1/60


type Callback[T] = Callable[[T], None]


# class EventTarget[T]:
#     listeners: set[Callback[T]]

#     def listen(self, callback: Callback[T]):
#         self.listeners.add(callback)

#     def unlisten(self, callback: Callback[T]):
#         self.listeners.remove(callback)

#     def dispatch(self, value: T):
#         for callback in self.listeners:
#             callback(value)


type EventType = str


class EventTarget[T]:
    @abstractmethod
    def dispatch(self, type: EventType, value: T) -> None: ...

    def mapped[U](self, f: Callable[[U], T]) -> "EventTarget[U]":
        return MappedEventTarget(self, f)


class MappedEventTarget[T, O](EventTarget[T]):
    orig: EventTarget[O]
    f: Callable[[T], O]

    def __init__(self, orig: EventTarget[O], f: Callable[[T], O]) -> None:
        super().__init__()
        self.orig = orig
        self.f = f

    def dispatch(self, type: EventType, value: T) -> None:
        self.orig.dispatch(type, self.f(value))


class EventBuffer[T](EventTarget[T]):
    """Prevents resending of same events by collecting only the last one."""

    events: dict[EventType, T] = {}

    def dispatch(self, type: EventType, value: T) -> None:
        self.events[type] = value

    def collect(self) -> Iterable[T]:
        events = self.events.values()
        self.events = {}
        return events


""" Thread-safe value """


class Atom[T]:
    _value: T
    _lock: Lock = Lock()

    def __init__(self, value: T) -> None:
        self.set(value)

    def get(self) -> T:
        with self._lock:
            return self._value

    def set(self, value: T) -> None:
        with self._lock:
            self._value = value


type IpV4 = int
type Message = Event
# time of arrival, message (Network internal)
type Packet = tuple[Time, Message]
# time of arrival, message
type TimedMessage = tuple[Time, Message]


class Network:
    """Thread-safe Network emulator"""

    delay = 0.1
    add_client_lock = Lock()
    clients: dict[IpV4, Queue[Packet]] = {}

    @staticmethod
    def add_client_if_missing(ip: IpV4):
        with Network.add_client_lock:
            if ip not in Network.clients:
                Network.clients[ip] = Queue()

    @staticmethod
    def send(ip: IpV4, msg: Message):
        Network.add_client_if_missing(ip)
        t_arrive = perf_counter() + 0.1
        Network.clients[ip].put((t_arrive, msg))

    @staticmethod
    def receive(ip: IpV4) -> deque[TimedMessage]:
        """receive a list of messages for this ip, oldest first"""
        Network.add_client_if_missing(ip)
        t = perf_counter()
        arrived = deque[Packet]()
        not_arrived = deque[Packet]()
        while True:
            try:
                packet = Network.clients[ip].get_nowait()
                t_arrive, _ = packet
                if t_arrive > t:
                    not_arrived.append(packet)
                else:
                    arrived.append(packet)
            except Empty:
                break
        for packet in not_arrived:
            Network.clients[ip].put(packet)
        return deque(sorted(arrived, key=lambda _: _[0]))


@dataclass(frozen=True)
class GameContex:
    entities: Entities


def gen_entity_id(ctx: "GameContex") -> EntityId:
    id: Optional[EntityId] = None
    while id == None:
        _id = getrandbits(32)
        if _id not in ctx.entities:
            id = _id
    return id


def gen_id(ids: Iterable[int]) -> int:
    while True:
        next_id = getrandbits(32)
        if next_id in ids:
            continue
        return next_id


@dataclass(frozen=True)
class Input:
    id: InputId
    move_right: bool
    move_down: bool
    move_left: bool
    move_up: bool
    action: bool


# Server to client events


@dataclass(frozen=True)
class ServerEvent[Evt](ABC):
    last_ack: InputId
    event: Evt


@dataclass(frozen=True)
class EntityEvent[Evt](ABC):
    entity: EntityId
    type: EventType
    event: Evt


@dataclass(frozen=True)
class CreateRobot:
    position: Vector2
    orientation: Vector2
    color: "Color"


@dataclass(frozen=True)
class MotionUpdate:
    position: Vector2
    orientation: Vector2


@dataclass(frozen=True)
class ColorUpdate:
    color: "Color"


# Client to server events


@dataclass(frozen=True)
class ClientEvent[Evt]:
    ack: InputId
    client: ClientId
    event: Evt


@dataclass(frozen=True)
class InputEvent:
    input: Input
    dt: Time


# Protocol events

""" Set ClientEvent.client to this value when sending ConnectionRequest

It will be ignored and the assigned id is send as ConnectionConfirm.client_id
"""
INITIAL_CLIENT_ID = -1


@dataclass(frozen=True)
class ConnectionRequest:
    ip: IpV4


@dataclass(frozen=True)
class ConnectionConfirm:
    client_id: ClientId
    client_entity: EntityId
    world: deque["S2CEntityEvent"]


# Event categories

type S2CUpdateEvent = MotionUpdate | ColorUpdate
type S2CEntityEvent = EntityEvent[CreateRobot | S2CUpdateEvent]
type S2CEvent = ServerEvent[S2CEntityEvent | ConnectionConfirm]
type C2SEvent = ClientEvent[ConnectionRequest | InputEvent]
type Event = S2CEvent | C2SEvent


class UpdatableValue[T](ABC):

    @abstractmethod
    def tick_client(self, input: Input, dt: Time, t: Time) -> None: ...
    @abstractmethod
    def on_server_update(self, value: T, last_ack: InputId, t_ack: Time) -> None: ...

    @property
    @abstractmethod
    def value(self) -> T: ...


class PredictedValue[T](UpdatableValue[T], ABC):
    # queue of t, input and dt
    predicted_inputs: deque[tuple[Time, Input, Time]] = deque()
    _value: T

    def __init__(self, value: T) -> None:
        super().__init__()
        self._value = value

    @abstractmethod
    def predict(self, current: T, input: Input, dt: Time, t: Time) -> T: ...

    def tick_client(
        self, input: Input, dt: Time, t: Time, replay: bool = False
    ) -> None:
        if replay == False:
            self.predicted_inputs.append((t, input, dt))
        self._value = self.predict(self._value, input, dt, t)

    def on_server_update(self, value: T, last_ack: InputId, t_ack: Time) -> None:
        self._value = value
        while (
            len(self.predicted_inputs) > 0
            and self.predicted_inputs[0][1].id <= last_ack
        ):
            # already respected by server snapshot, so remove
            self.predicted_inputs.popleft()
        for t, input, dt in self.predicted_inputs:
            self.tick_client(input, dt, t, replay=True)

    @property
    def value(self) -> T:
        return self._value


class InterpolatedValue[T](UpdatableValue[T], ABC):
    """"""

    """snapshots of receiced time and data

    invariant: len(snapshots) >= 1
    """
    snapshots: deque[tuple[Time, T]]
    _value: T

    def __init__(self, value: T, t: Time) -> None:
        super().__init__()
        self._value = value
        self.snapshots = deque([(t, value)])

    @abstractmethod
    def interpolate(self, old: T, new: T, blend: float) -> T: ...

    def tick_client(self, input: Input, dt: Time, t: Time) -> None:
        interpolated_t = t - SERVER_TIMESTEP

        # delete old snapshots
        # snapshots of the current frame are considered old snapshots for easier interpolation
        while len(self.snapshots) >= 2 and self.snapshots[1][0] <= interpolated_t:
            self.snapshots.popleft()
        if self.snapshots[0][0] > interpolated_t:
            # only future snapshot available
            # this should not happen, since __init__ adds old snapshot
            raise ValueError("interpolated value: only future snapshot")

        # now the first snapshot is in the past or present
        #     the rest (if any) are in the future

        if len(self.snapshots) == 1:
            # only old snapshot available, use this snapshot
            self._value = self.snapshots[0][1]
            return
        # past and future available, interpolate
        old, t_old = self.snapshots[0][1], self.snapshots[0][0]
        new, t_new = self.snapshots[1][1], self.snapshots[1][0]
        blend = (interpolated_t - t_old) / (t_new - t_old)
        self._value = self.interpolate(old, new, blend)

    def on_server_update(self, value: T, last_ack: InputId, t_ack: Time) -> None:
        # insert right of existing entries to preserve ordering
        # even when multiple snapshots arrive in the same tick
        insort_right(self.snapshots, (t_ack, value), key=lambda _: _[0])

    @property
    def value(self) -> T:
        return self._value


class ExtrapolatedValue[T](UpdatableValue[T], ABC):
    last_snapshot: tuple[Time, T]
    _value: T

    def __init__(self, value: T, t: Time) -> None:
        super().__init__()
        self.last_snapshot = (t, value)

    @abstractmethod
    def extrapolate(self, value: T, dt: Time) -> T: ...

    def tick_client(self, input: Input, dt: Time, t: Time) -> None:
        self._value = self.extrapolate(self.last_snapshot[1], self.last_snapshot[0])

    def on_server_update(self, value: T, last_ack: InputId, t_ack: Time) -> None:
        self.last_snapshot = (t_ack, value)

    @property
    def value(self) -> T:
        return self._value


class RemoteValue[T](UpdatableValue[T]):
    _value: T

    def __init__(self, value: T) -> None:
        super().__init__()
        self._value = value

    def tick_client(self, input: Input, dt: Time, t: Time) -> None:
        pass

    def on_server_update(self, value: T, last_ack: InputId, t_ack: Time) -> None:
        self._value = value

    @property
    def value(self) -> T:
        return self._value


# Base entity interface


class Entity(ABC):
    id: EntityId
    # If set, the entity is not acknoledged by the server
    predicted: Optional[InputId]

    def __init__(self, id: EntityId) -> None:
        super().__init__()
        self.id = id

    @abstractmethod
    def tick_client(self, input: Input, dt: Time, t: Time): ...

    @abstractmethod
    def on_server_event(
        self,
        event_type: EventType,
        event: S2CUpdateEvent,
        last_ack: InputId,
        t_ack: Time,
    ) -> None: ...


# Interfaces for different properties

type Position = Vector2
type Orientation = Vector2
type Motion = tuple[Position, Orientation]


class MotionEntity(Entity, ABC):
    # don't mutate!
    motion: UpdatableValue[Motion]


type Color = pygame.Color


class ColorEntity(Entity, ABC):
    # don't mutate!
    color: UpdatableValue[Color]


# Entity client implementations


class PlayerRobot(MotionEntity, ColorEntity):
    # don't mutate!
    motion: PredictedValue[Motion]
    # don't mutate!
    color: RemoteValue[Color]

    class PredictedMotion(PredictedValue[Motion]):

        def predict(self, current: Motion, input: Input, dt: Time, t: Time) -> Motion:
            cur_position, cur_orientation = current

            new_orientation = Vector2(0, 0)
            if input.move_right:
                new_orientation += Vector2(1, 0)
            if input.move_down:
                new_orientation += Vector2(0, 1)
            if input.move_left:
                new_orientation += Vector2(-1, 0)
            if input.move_up:
                new_orientation += Vector2(0, -1)
            if new_orientation.length() != 0:
                new_orientation.normalize()

            new_position = cur_position + dt * new_orientation
            cached_orientation = (
                new_orientation
                if not (new_orientation == Vector2(0, 0))
                else cur_orientation
            )
            return (new_position, cached_orientation)

    def __init__(self, id: EntityId, motion: Motion, color: Color, t: Time) -> None:
        super().__init__(id)
        self.motion = self.PredictedMotion(motion)  # type: ignore
        self.color = RemoteValue(color)  # type: ignore

    def tick_client(self, input: Input, dt: Time, t: Time):
        self.motion.tick_client(input, dt, t)
        self.color.tick_client(input, dt, t)

    def on_server_event(
        self,
        event_type: EventType,
        event: S2CUpdateEvent,
        last_ack: InputId,
        t_ack: Time,
    ) -> None:
        match (event_type, event):
            case ("motion", MotionUpdate()):
                self.motion.on_server_update(
                    (event.position, event.orientation), last_ack, t_ack
                )
            case ("color", ColorUpdate()):
                self.color.on_server_update(event.color, last_ack, t_ack)
            case _:
                raise ValueError("entity: invalid event")


class EnemyRobot(MotionEntity, ColorEntity):
    # don't mutate!
    motion: InterpolatedValue[Motion]
    # don't mutate!
    color: RemoteValue[Color]

    class InterpolatedMotion(InterpolatedValue[Motion]):

        def interpolate(self, old: Motion, new: Motion, blend: float) -> Motion:
            return (
                old[0] + (new[0] - old[0]) * blend,
                old[1] + (new[1] - old[1]) * blend,
            )

    def __init__(self, id: EntityId, motion: Motion, color: Color, t: Time) -> None:
        super().__init__(id)
        self.motion = self.InterpolatedMotion(motion, t)  # type: ignore
        self.color = RemoteValue(color)  # type: ignore

    def tick_client(self, input: Input, dt: Time, t: Time):
        self.motion.tick_client(input, dt, t)
        self.color.tick_client(input, dt, t)

    def on_server_event(
        self,
        event_type: EventType,
        event: S2CUpdateEvent,
        last_ack: InputId,
        t_ack: Time,
    ) -> None:
        match (event_type, event):
            case ("motion", MotionUpdate()):
                self.motion.on_server_update(
                    (event.position, event.orientation), last_ack, t_ack
                )
            case ("color", ColorUpdate()):
                self.color.on_server_update(event.color, last_ack, t_ack)
            case _:
                raise ValueError("entity: invalid event")


type EntityType = EnemyRobot | PlayerRobot

# Entity server implementations

type SendEventFn[Evt] = Callable[[EventType, Evt], None]
type SimpleSendEventFn[Evt] = Callable[[Evt], None]


class UpdatingValue[T, Evt, Info](ABC):
    send_event: SimpleSendEventFn[Evt]

    def __init__(self, send_event: SimpleSendEventFn[Evt]) -> None:
        super().__init__()
        self.send_event = send_event

    @abstractmethod
    def tick_server(self, dt: Time, info: Info) -> None: ...

    @property
    @abstractmethod
    def value(self) -> T: ...


class SimulatedValue[T, Evt, Info](UpdatingValue[T, Evt, Info], ABC):
    _value: T

    def __init__(self, value: T, send_event: SimpleSendEventFn[Evt]) -> None:
        super().__init__(send_event)
        self._value = value

    @abstractmethod
    def simulate(self, current: T, dt: Time, info: Info) -> T: ...

    @abstractmethod
    def gen_event(self, value: T) -> Evt: ...

    def tick_server(self, dt: Time, info: Info) -> None:
        self._value = self.simulate(self._value, dt, info)
        event = self.gen_event(self._value)
        self.send_event(event)

    @property
    def value(self) -> T:
        return self._value


class ControllingValue[T, Evt](UpdatingValue[T, Evt, None], ABC):
    _value: T

    def __init__(self, value: T, send_event: SimpleSendEventFn[Evt]) -> None:
        super().__init__(send_event)
        self._value = value

    @abstractmethod
    def gen_event(self, value: T) -> Evt: ...

    def set(self, value: T) -> None:
        if value == self.value:
            return
        self._value = value
        self.send_event(self.gen_event(value))

    def tick_server(self, dt: Time, info: None) -> None:
        pass

    @property
    def value(self) -> T:
        return self._value


class ServerEntity(ABC):
    id: EntityId
    _send_event: SendEventFn[S2CEntityEvent]

    def __init__(self, id: EntityId, send_event: SendEventFn[S2CEntityEvent]) -> None:
        super().__init__()
        self.id = id
        self._send_event = send_event

    def send_event(self, event_type: EventType, event: S2CUpdateEvent) -> None:
        new_event_type = str(self.id) + "/" + event_type
        self._send_event(new_event_type, EntityEvent(self.id, event_type, event))

    @abstractmethod
    def tick_server(self, dt: Time): ...


class InputServerEntity(ServerEntity, ABC):
    @abstractmethod
    def tick_server(self, dt: Time, *, input: Optional[Input] = None): ...


class MotionServerEntity[Info](ServerEntity, ABC):
    # don't mutate!
    motion: UpdatingValue[Motion, MotionUpdate, Info]


class ColorServerEntity[Info](ServerEntity, ABC):
    # don't mutate!
    color: UpdatingValue[Color, ColorUpdate, Info]


class PlayerServerRobot(
    InputServerEntity,
    MotionServerEntity[tuple[Optional[Input]]],
    ColorServerEntity[None],
):
    # don't mutate!
    motion: SimulatedValue[Motion, MotionUpdate, tuple[Optional[Input]]]
    # don't mutate!
    color: ControllingValue[Color, ColorUpdate]

    class SendingMotion(SimulatedValue[Motion, MotionUpdate, tuple[Optional[Input]]]):

        def simulate(
            self, current: Motion, dt: Time, info: tuple[Optional[Input]]
        ) -> Motion:
            (input,) = info
            if input == None:
                return current
            cur_position, cur_orientation = current

            new_orientation = Vector2(0, 0)
            if input.move_right:
                new_orientation += Vector2(1, 0)
            if input.move_down:
                new_orientation += Vector2(0, 1)
            if input.move_left:
                new_orientation += Vector2(-1, 0)
            if input.move_up:
                new_orientation += Vector2(0, -1)
            if new_orientation.length() != 0:
                new_orientation.normalize()

            new_position = cur_position + dt * new_orientation
            cached_orientation = (
                new_orientation
                if not (new_orientation == Vector2(0, 0))
                else cur_orientation
            )
            return (new_position, cached_orientation)

        def gen_event(self, value: Motion) -> MotionUpdate:
            return MotionUpdate(value[0], value[1])

    class ControllingColor(ControllingValue[Color, ColorUpdate]):
        def gen_event(self, value: Color) -> ColorUpdate:
            return ColorUpdate(value)

    def __init__(
        self,
        id: EntityId,
        motion: Motion,
        color: Color,
        send_event: SendEventFn[S2CEntityEvent],
    ) -> None:
        super().__init__(id, send_event)
        self.motion = self.SendingMotion(motion, partial(self.send_event, "motion"))  # type: ignore
        self.color = self.ControllingColor(  # type: ignore
            color, partial(self.send_event, "color")
        )

    def tick_server(self, dt: Time, *, input: Optional[Input] = None):
        self.motion.tick_server(dt, (input,))
        self.color.tick_server(dt, None)


class EnemyServerRobot(MotionServerEntity[None], ColorServerEntity[None]):
    # don't mutate!
    motion: SimulatedValue[Motion, MotionUpdate, None]
    # don't mutate!
    color: ControllingValue[Color, ColorUpdate]

    class SendingMotion(SimulatedValue[Motion, MotionUpdate, None]):
        initial_position: Position

        def __init__(
            self,
            value: Motion,
            send_event: SimpleSendEventFn[MotionUpdate],
        ) -> None:
            super().__init__(value, send_event)
            self.initial_position = value[0]

        def simulate(self, current: Motion, dt: Time, info: None) -> Motion:
            pos, ori = current
            new_ori = ori * -1 if pos.distance_to(self.initial_position) > 3 else ori
            new_pos = pos + new_ori * dt
            return (new_pos, new_ori)

        def gen_event(self, value: Motion) -> MotionUpdate:
            return MotionUpdate(value[0], value[1])

    class ControllingColor(ControllingValue[Color, ColorUpdate]):
        def gen_event(self, value: Color) -> ColorUpdate:
            return ColorUpdate(value)

    def __init__(
        self,
        id: EntityId,
        motion: Motion,
        color: Color,
        send_event: SendEventFn[S2CEntityEvent],
    ) -> None:
        super().__init__(id, send_event)
        self.motion = self.SendingMotion(motion, partial(self.send_event, "motion"))  # type: ignore
        self.color = self.ControllingColor(  # type: ignore
            color, partial(self.send_event, "color")
        )

    def tick_server(self, dt: Time):
        self.motion.tick_server(dt, None)
        self.color.tick_server(dt, None)


type ServerEntityType = PlayerServerRobot | EnemyServerRobot


class Client:
    server: "Server"
    input_id: InputId = 0
    last_ack: InputId
    ip: IpV4
    id: ClientId
    entity: EntityId

    entities: dict[EntityId, EntityType] = {}

    def __init__(self, ip: IpV4):
        # init values
        self.ip = ip

        # connect to server
        ack = self.input_id
        self.input_id += 1
        self.send_server(
            ClientEvent(ack, INITIAL_CLIENT_ID, ConnectionRequest(self.ip))
        )
        # wait for connection confirmation
        while True:
            messages = self.receive_server()
            if len(messages) == 0:
                continue
            t_msg, msg = messages.popleft()
            if not isinstance(msg, ServerEvent):
                raise ValueError("client: message not ServerEvent")
            if not isinstance(msg.event, ConnectionConfirm):
                raise ValueError("client: event not ConnectionEvent")
            self.last_ack = msg.last_ack
            self.id = msg.event.client_id
            self.entity = msg.event.client_entity
            self.handle_messages(
                map(lambda _: (t_msg, ServerEvent(msg.last_ack, _)), msg.event.world)
            )
            break

        # run main loop
        self.loop()

    def handle_messages(self, messages: Iterable[TimedMessage]):
        for t_msg, msg in messages:
            if not isinstance(msg, ServerEvent):
                raise ValueError("handle_messages: not ServerEvent")
            if not isinstance(msg.event, EntityEvent):
                raise ValueError("handle_messages: not EntityEvent")
            last_ack = msg.last_ack
            entity = msg.event.entity
            type = msg.event.type
            event = msg.event.event

            self.last_ack = max(self.last_ack, last_ack)
            if isinstance(event, CreateRobot):
                entity = (
                    PlayerRobot(
                        entity, (event.position, event.orientation), event.color, t_msg
                    )
                    if entity == self.entity
                    else EnemyRobot(
                        entity, (event.position, event.orientation), event.color, t_msg
                    )
                )
                self.entities[entity.id] = entity
                continue
            self.entities[entity].on_server_event(type, event, last_ack, t_msg)

    def send_server(self, message: C2SEvent) -> None:
        Network.send(SERVER_IP, message)

    def receive_server(self) -> deque[TimedMessage]:
        return Network.receive(self.ip)

    def send_input(
        self,
        input: Input,
        dt: Time,
    ):
        ack = self.input_id
        self.input_id += 1
        self.send_server(ClientEvent(ack, self.id, InputEvent(input, dt)))

    def get_input(self):
        input_id = self.input_id
        self.input_id += 1

        keys = pygame.key.get_pressed()
        return Input(
            id=input_id,
            move_right=keys[pygame.K_RIGHT],
            move_down=keys[pygame.K_DOWN],
            move_left=keys[pygame.K_LEFT],
            move_up=keys[pygame.K_UP],
            action=keys[pygame.K_a],
        )

    def render(self, display: Surface, entities: Iterable[EntityType]) -> None:
        for entity in entities:
            match entity:
                case PlayerRobot():
                    pygame.draw.circle(
                        display,
                        entity.color.value,
                        entity.motion.value[0] * PIXELS_PER_BLOCK,
                        0.5 * PIXELS_PER_BLOCK,
                    )
                case EnemyRobot():
                    pygame.draw.circle(
                        display,
                        entity.color.value,
                        entity.motion.value[0] * PIXELS_PER_BLOCK,
                        0.5 * PIXELS_PER_BLOCK,
                    )

    def loop(self):
        last_t = perf_counter()
        clock = pygame.time.Clock()

        pygame.init()
        screen = pygame.display.set_mode((1000, 1000))
        while True:
            # init frame
            t = perf_counter()
            dt = t - last_t

            self.handle_messages(self.receive_server())

            input = self.get_input()
            self.send_input(input, dt)

            for _, entity in self.entities.items():
                entity.tick_client(input, dt, t)

            # rendering
            pygame.event.pump()
            screen.fill("black")
            self.render(screen, self.entities.values())
            pygame.display.flip()
            print("rendered")

            # cleanup frame
            last_t = t
            clock.tick(CLIENT_FRAMERATE)


@dataclass
class ClientInfo:
    ip: IpV4
    last_ack: InputId
    entity: InputServerEntity
    events: EventBuffer[S2CEvent] = EventBuffer()


class Receiver:
    """Receiver is running constantly in seperate thread

    Enables messages to be tagged with exact time of arrival
    """

    _ip: IpV4
    _received: Queue[TimedMessage] = Queue()
    _deleted: Atom[bool] = Atom(False)

    def __init__(self, ip: IpV4) -> None:
        self._ip = ip
        Thread(target=self.receive_loop, args=()).start()

    def __del__(self) -> None:
        self._deleted.set(True)

    def received(self) -> deque[TimedMessage]:
        received = deque[TimedMessage]()
        while True:
            try:
                received.append(self._received.get_nowait())
            except Empty:
                break
        return deque(sorted(received, key=lambda _: _[0]))

    def received_until(self, t: Time) -> deque[TimedMessage]:
        received = deque[TimedMessage]()
        not_received = deque[TimedMessage]()
        while True:
            try:
                msg = self._received.get_nowait()
                if msg[0] > t:
                    not_received.append(msg)
                else:
                    received.append(msg)
            except Empty:
                break
        for msg in not_received:
            self._received.put(msg)
        return deque(sorted(received, key=lambda _: _[0]))

    def receive_loop(self):
        while not self._deleted.get():
            messages = Network.receive(self._ip)
            for msg in messages:
                self._received.put(msg)


class Server:
    clients: dict[ClientId, ClientInfo] = {}
    ip: IpV4
    receiver: Receiver

    entities: dict[EntityId, ServerEntityType]

    def __init__(self, ip: IpV4) -> None:
        self.ip = ip
        self.receiver = Receiver(self.ip)

        enemy_id = 0
        enemy = EnemyServerRobot(
            enemy_id,
            (Vector2(10, 1), Vector2(1, 0)),
            pygame.Color(255, 0, 0),
            partial(self.send_event, None),
        )
        self.entities = {enemy_id: enemy}

        self.loop()

    def send_event(
        self,
        client: Optional[ClientId],
        even_type: EventType,
        event: ConnectionConfirm | S2CEntityEvent,
    ):
        targets_ids = [client] if client != None else self.clients.keys()
        for target_id in targets_ids:
            target = self.clients[target_id]
            target.events.dispatch(even_type, ServerEvent(target.last_ack, event))

    def handle_messages(
        self, messages: Sequence[TimedMessage]
    ) -> Sequence[tuple[ClientId, InputEvent]]:
        """handle incoming messages

        Return input events, which are validated and the acknoledgment registered
        """
        input_events = deque[tuple[ClientId, InputEvent]]()
        for _, msg in messages:
            if not isinstance(msg, ClientEvent):
                raise ValueError("handle_messages: not ClientEvent")
            if isinstance(msg.event, ConnectionRequest):
                client_id = gen_id(self.clients.keys())
                client_entity = self.gen_client_entity(client_id)
                client = ClientInfo(msg.event.ip, msg.ack, client_entity)
                self.entities[client_entity.id] = client_entity
                self.clients[client_id] = client
                self.send_event(
                    client_id,
                    "ConnectionConfirm",
                    ConnectionConfirm(
                        client_id, client_entity.id, self.world_as_messages()
                    ),
                )
                continue

            self.clients[msg.client].last_ack = msg.ack
            if isinstance(msg.event, InputEvent):  # type: ignore
                input_events.append((msg.client, msg.event))
        return input_events

    def gen_client_entity(self, client: ClientId) -> PlayerServerRobot:
        id = gen_id(self.entities.keys())
        entity = PlayerServerRobot(
            id,
            (Vector2(10, 5), Vector2(1, 0)),
            pygame.Color(0, 255, 0),
            lambda t, e: self.send_event(client, t, e),
        )
        return entity

    def world_as_messages(self) -> deque[S2CEntityEvent]:
        def entity_as_event(entity: ServerEntityType) -> S2CEntityEvent:
            match entity:
                case PlayerServerRobot():
                    create = CreateRobot(
                        entity.motion.value[0],
                        entity.motion.value[1],
                        entity.color.value,
                    )
                    return EntityEvent(entity.id, "", create)
                case EnemyServerRobot():
                    create = CreateRobot(
                        entity.motion.value[0],
                        entity.motion.value[1],
                        entity.color.value,
                    )
                    return EntityEvent(entity.id, "", create)

        return deque(map(entity_as_event, self.entities.values()))

    def render(self, display: Surface, entities: Iterable[ServerEntityType]) -> None:
        for entity in entities:
            match entity:
                case PlayerServerRobot():
                    pygame.draw.circle(
                        display,
                        entity.color.value,
                        entity.motion.value[0] * PIXELS_PER_BLOCK,
                        0.5 * PIXELS_PER_BLOCK,
                    )
                case EnemyServerRobot():
                    pygame.draw.circle(
                        display,
                        entity.color.value,
                        entity.motion.value[0] * PIXELS_PER_BLOCK,
                        0.5 * PIXELS_PER_BLOCK,
                    )

    def loop(self) -> None:
        last_t = perf_counter()
        clock = pygame.time.Clock()

        # pygame.init()
        # screen = pygame.display.set_mode((1000, 1000))
        while True:
            # init update
            t_update = perf_counter()
            dt_update = t_update - last_t
            dt_frame = dt_update / SERVER_FRAMES_PER_TIMESTEP

            # Each update is split into 3 frames to get more precise results
            for i in range(SERVER_FRAMES_PER_TIMESTEP):
                t_frame = last_t + i * dt_frame

                received = self.receiver.received_until(t_frame)
                inputs = self.handle_messages(received)

                for client, input in inputs:
                    self.clients[client].entity.tick_server(input.dt, input=input.input)

                for _, entity in self.entities.items():
                    entity.tick_server(dt_frame)

            # # rendering
            # pygame.event.pump()
            # screen.fill("black")
            # self.render(screen, self.entities.values())
            # pygame.display.flip()
            # print("rendered")

            # send events to clients
            for client in self.clients.values():
                for evt in client.events.collect():
                    Network.send(client.ip, evt)

            # cleanup udpate
            last_t = t_update
            clock.tick(1 / SERVER_TIMESTEP)


Thread(target=Server, args=(SERVER_IP,)).start()
client = Client(1234)
