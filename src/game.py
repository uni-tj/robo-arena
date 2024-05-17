from abc import ABC, abstractmethod
from bisect import insort_right
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import partial
from queue import Empty, Queue
from random import getrandbits
from threading import Lock, Thread
from time import perf_counter
from typing import (
    Callable,
    Optional,
)

import pygame
from pygame import Color, Surface, Vector2

type EntityId = int
type Entities = dict[EntityId, Entity]
type Acknoledgement = int
type ClientId = int
type Time = float

SERVER_TIMESTEP = 1 / 20
CLIENT_TIMESTEP = 1 / 60
SERVER_FRAMES_PER_TIMESTEP = 3
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


def px[T: int | Vector2 | float](unit: T) -> T:
    """Calculate px from game units"""
    match unit:
        case Vector2():
            return unit * PIXELS_PER_BLOCK
        case int():
            return unit * PIXELS_PER_BLOCK  # type: ignore
        case float():
            return unit * PIXELS_PER_BLOCK  # type: ignore


type EventName = str


class EventTarget[T]:
    @abstractmethod
    def dispatch(self, type: EventName, value: T) -> None: ...

    def mapped[U](self, f: Callable[[U], T]) -> "EventTarget[U]":
        return MappedEventTarget(self, f)


class MappedEventTarget[T, O](EventTarget[T]):
    orig: EventTarget[O]
    f: Callable[[T], O]

    def __init__(self, orig: EventTarget[O], f: Callable[[T], O]) -> None:
        super().__init__()
        self.orig = orig
        self.f = f

    def dispatch(self, type: EventName, value: T) -> None:
        self.orig.dispatch(type, self.f(value))


class EventBuffer[T](EventTarget[T]):
    """Prevents resending of same events by collecting only the last one."""

    events: dict[EventName, T] = {}

    def dispatch(self, type: EventName, value: T) -> None:
        self.events[type] = value

    def collect(self) -> Iterable[T]:
        events = self.events.values()
        self.events = {}
        return events


class Atom[T]:
    """Thread-safe value"""

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
type Message = EventType
# time of arrival, message (Network internal)
type Packet = tuple[Time, Message]
# time of arrival, message
type TimedMessage = tuple[Time, Message]


def time() -> Time:
    """Get the reference time.

    Only the difference in seconds is valid.
    """
    return perf_counter()


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
    while id is None:
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


def counter():
    next = 0
    while True:
        yield next
        next += 1


type ServerSubEventType = (
    ServerConnectionConfirmEvent | ServerSpawnRobotEvent | ServerEntityEvent
)
type ServerEventType = ServerEvent[ServerSubEventType]
type ClientSubEventType = ClientConnectionRequestEvent | ClientInputEvent
type ClientEventType = ClientEvent[ClientSubEventType]
type EventType = ServerEventType | ClientEventType

type OnEvent[Evt] = Callable[[EventName, Evt], None]
type SimpleOnEvent[Evt] = Callable[[Evt], None]

type Position = Vector2
type Orientation = Vector2
type Motion = tuple[Position, Orientation]


def interpolateMotion(old: Motion, new: Motion, blend: float, ctx: None) -> Motion:
    return (
        old[0] + (new[0] - old[0]) * blend,
        old[1] + (new[1] - old[1]) * blend,
    )


@dataclass(frozen=True)
class Input:
    move_right: bool
    move_down: bool
    move_left: bool
    move_up: bool
    action: bool


# Server to client events


@dataclass(frozen=True)
class ServerEvent[Evt](ABC):
    last_ack: Acknoledgement
    event: Evt


@dataclass(frozen=True)
class ServerConnectionConfirmEvent:
    client_id: ClientId
    client_entity: EntityId
    world: Iterable[ServerSubEventType]


@dataclass(frozen=True)
class ServerEntityEvent(ABC):
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


# Event categories


class Value[T](ABC):

    # @abstractmethod
    # def tick(self, dt: Time, t: Time): ...

    # @abstractmethod
    # def on_input(self, input: Input, dt: Time): ...

    @abstractmethod
    def get(self) -> T: ...


class UpdatableValue[T](ABC):

    @abstractmethod
    def tick_client(self, input: Input, dt: Time, t: Time) -> None: ...

    @abstractmethod
    def on_server_update(
        self, value: T, last_ack: Acknoledgement, t_ack: Time
    ) -> None: ...

    @property
    @abstractmethod
    def value(self) -> T: ...


class PredictedValue[T, Ctx](Value[T]):
    # queue of ack and ctx
    predicted_inputs: deque[tuple[Acknoledgement, Ctx]] = deque()
    # pars: current, dt, t, ctx
    predict: Callable[[T, Ctx], T]
    value: T

    def __init__(self, value: T, f: Callable[[T, Ctx], T]) -> None:
        super().__init__()
        self.value = value
        self.predict = f

    def on_input(
        self,
        ctx: Ctx,
        ack: Acknoledgement,
    ) -> None:
        self.predicted_inputs.append((ack, ctx))
        self.value = self.predict(self.value, ctx)

    def on_server(self, value: T, last_ack: Acknoledgement) -> None:
        self.value = value
        while (
            len(self.predicted_inputs) > 0 and self.predicted_inputs[0][0] <= last_ack
        ):
            # already respected by server snapshot, so remove
            self.predicted_inputs.popleft()
        for _, ctx in self.predicted_inputs:
            self.value = self.predict(self.value, ctx)

    def get(self) -> T:
        return self.value


class InterpolatedValue[T, Ctx](Value[T]):

    value: T
    interpolate: Callable[[T, T, float, Ctx], T]
    """snapshots of receiced time and data

    oldest first, newest last
    invariant: len(snapshots) >= 1
    """
    snapshots: deque[tuple[Acknoledgement, Time, T]]

    def __init__(
        self,
        value: T,
        last_ack: Acknoledgement,
        t: Time,
        f: Callable[[T, T, float, Ctx], T],
    ) -> None:
        super().__init__()
        self.value = value
        self.interpolate = f
        self.snapshots = deque([(last_ack, t, value)])

    def tick(self, t: Time, ctx: Ctx) -> None:
        interpolated_t = t - SERVER_TIMESTEP

        # delete old snapshots
        # snapshots of the current frame trated as old snapshots bc easier interpolation
        while len(self.snapshots) >= 2 and self.snapshots[1][1] <= interpolated_t:
            self.snapshots.popleft()
        if self.snapshots[0][1] > interpolated_t:
            # only future snapshot available
            # this should not happen, since __init__ adds old snapshot
            raise ValueError("interpolated value: only future snapshot")

        # now the first snapshot is in the past or present
        #     the rest (if any) are in the future

        if len(self.snapshots) == 1:
            # only old snapshot available, use this snapshot
            self.value = self.snapshots[0][2]
            return
        # past and future available, interpolate
        old, t_old = self.snapshots[0][2], self.snapshots[0][1]
        new, t_new = self.snapshots[1][2], self.snapshots[1][1]
        blend = (interpolated_t - t_old) / (t_new - t_old)
        self.value = self.interpolate(old, new, blend, ctx)

    def on_server(self, value: T, last_ack: Acknoledgement, t_ack: Time) -> None:
        # insert right of existing entries to preserve ordering
        # even when multiple snapshots arrive in the same tick
        insort_right(self.snapshots, (last_ack, t_ack, value), key=lambda _: _[0])

    def get(self) -> T:
        return self.value


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

    def on_server_update(self, value: T, last_ack: Acknoledgement, t_ack: Time) -> None:
        self.last_snapshot = (t_ack, value)

    @property
    def value(self) -> T:
        return self._value


class PassiveRemoteValue[T](Value[T]):
    value: T

    def __init__(self, value: T) -> None:
        super().__init__()
        self.value = value

    def on_server(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


class ActiveRemoteValue[T](Value[T]):
    value: T
    on_event: SimpleOnEvent[T]

    def __init__(self, value: T, on_event: SimpleOnEvent[T]) -> None:
        self.value = value
        self.on_event = on_event

    def set(self, value: T) -> None:
        if value == self.value:
            return
        self.value = value
        self.on_event(value)

    def get(self) -> T:
        return self.value


class CalculatedValue[T, Ctx](Value[T]):
    value: T
    calculate: Callable[[T, Ctx], T]
    on_event: SimpleOnEvent[T]

    def __init__(
        self, value: T, calculate: Callable[[T, Ctx], T], on_event: SimpleOnEvent[T]
    ) -> None:
        self.value = value
        self.calculate = calculate
        self.on_event = on_event

    def tick(self, ctx: Ctx) -> None:
        self.value = self.calculate(self.value, ctx)
        self.on_event(self.value)

    def get(self) -> T:
        return self.value


# Base entity interface


class Entity(ABC):
    @abstractmethod
    def tick(self, dt: Time, t: Time): ...

    @abstractmethod
    def render(self, surface: Surface) -> None: ...


class ServerInputHandler(ABC):
    @abstractmethod
    def on_input(self, input: Input, dt: Time): ...


class ClientInputHandler(ABC):
    @abstractmethod
    def on_input(self, input: Input, dt: Time, ack: Acknoledgement): ...


class ClientEntity(Entity, ABC):

    @abstractmethod
    def on_server(
        self,
        event_name: EventName,
        event: object,
        last_ack: Acknoledgement,
        t_ack: Time,
    ): ...


type PlayerRobotMoveCtx = tuple[Input, Time]


class PlayerRobot(Entity):
    motion: Value[Motion]
    color: Value[Color]

    def move(self, current: Motion, ctx: PlayerRobotMoveCtx) -> Motion:
        input, dt = ctx
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

        new_position = cur_position + dt * new_orientation * 5
        cached_orientation = (
            new_orientation
            if not (new_orientation == Vector2(0, 0))
            else cur_orientation
        )
        return (new_position, cached_orientation)

    def render(self, surface: Surface) -> None:
        pygame.draw.circle(
            surface,
            self.color.get(),
            px(self.motion.get()[0]),
            px(0.5),
        )


class ClientPlayerRobot(PlayerRobot, ClientEntity, ClientInputHandler):
    motion: PredictedValue[Motion, PlayerRobotMoveCtx]
    color: PassiveRemoteValue[Color]

    def __init__(self, motion: Motion, color: Color) -> None:
        self.motion = PredictedValue(motion, self.move)  # type: ignore
        self.color = PassiveRemoteValue(color)  # type: ignore

    def on_input(self, input: Input, dt: Time, ack: Acknoledgement):
        self.motion.on_input((input, dt), ack)
        pass

    def on_server(
        self,
        event_name: EventName,
        event: object,
        last_ack: Acknoledgement,
        t_ack: Time,
    ):
        match event_name, event:
            case "motion", tuple((Vector2(), Vector2()) as e):
                self.motion.on_server(e, last_ack)
                pass
            case "color", Color():
                self.color.on_server(event)
            case _:
                raise ValueError("entity: invalid event")

    def tick(self, dt: Time, t: Time):
        pass


class ServerPlayerRobot(PlayerRobot, ServerInputHandler):
    motion: CalculatedValue[Motion, PlayerRobotMoveCtx]
    color: ActiveRemoteValue[Color]

    def __init__(
        self, motion: Motion, color: Color, on_event: OnEvent[Motion | Color]
    ) -> None:
        self.motion = CalculatedValue(motion, self.move, partial(on_event, "motion"))  # type: ignore
        self.color = ActiveRemoteValue(color, partial(on_event, "color"))  # type: ignore

    def on_input(self, input: Input, dt: Time):
        self.motion.tick((input, dt))

    def tick(self, dt: Time, t: Time):
        pass


type EnemyRobotMoveCtx = tuple[Time]


class EnemyRobot(Entity):
    motion: Value[Motion]
    color: Value[Color]
    initial_position: Position

    def __init__(self, motion: Motion) -> None:
        self.initial_position = motion[0]

    def move(self, current: Motion, ctx: EnemyRobotMoveCtx) -> Motion:
        (dt,) = ctx
        pos, ori = current
        new_ori = ori * -1 if pos.distance_to(self.initial_position) > 3 else ori
        new_pos = pos + new_ori * dt
        return (new_pos, new_ori)

    def render(self, surface: Surface) -> None:
        pygame.draw.circle(
            surface,
            self.color.get(),
            px(self.motion.get()[0]),
            px(0.5),
        )


class ClientEnemyRobot(EnemyRobot, ClientEntity):
    motion: InterpolatedValue[Motion, None]
    color: PassiveRemoteValue[Color]

    def __init__(
        self, motion: Motion, color: Color, last_ack: Acknoledgement, t_ack: Time
    ) -> None:
        self.motion = InterpolatedValue(motion, last_ack, t_ack, interpolateMotion)  # type: ignore
        self.color = PassiveRemoteValue(color)  # type: ignore

    def on_server(
        self,
        event_name: EventName,
        event: object,
        last_ack: Acknoledgement,
        t_ack: Time,
    ):
        match event_name, event:
            case "motion", tuple((Vector2(), Vector2()) as e):
                self.motion.on_server(e, last_ack, t_ack)
            case "color", Color():
                self.color.on_server(event)
            case _:
                raise ValueError("entity: invalid event")

    def tick(self, dt: Time, t: Time):
        self.motion.tick(t, None)


class ServerEnemyRobot(EnemyRobot):
    motion: CalculatedValue[Motion, EnemyRobotMoveCtx]
    color: ActiveRemoteValue[Color]

    def __init__(
        self, motion: Motion, color: Color, on_event: OnEvent[Motion | Color]
    ) -> None:
        super().__init__(motion)
        self.motion = CalculatedValue(  # type: ignore
            motion, self.move, partial(on_event, "motion")
        )
        self.color = ActiveRemoteValue(color, partial(on_event, "color"))  # type: ignore

    def tick(self, dt: Time, t: Time):
        self.motion.tick((dt,))


type ClientEntityType = ClientPlayerRobot | ClientEnemyRobot


class Client:
    ack = counter()
    ip: IpV4
    id: ClientId = INITIAL_CLIENT_ID
    entity_id: EntityId
    entity: ClientInputHandler

    entities: dict[EntityId, ClientEntityType] = {}

    def __init__(self, ip: IpV4):
        # init values
        self.ip = ip

        # connect to server
        self.on_event(ClientConnectionRequestEvent(self.ip))
        # wait for connection confirmation
        while True:
            messages = self.fetch_events()
            if len(messages) == 0:
                continue
            t_msg, msg = messages.popleft()
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
            self.handle_events(messages)
            break

        # run main loop
        self.loop()

    def handle_events(self, messages: Iterable[TimedMessage]):
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

    def on_event(self, event: ClientSubEventType) -> Acknoledgement:
        ack = next(self.ack)
        Network.send(
            SERVER_IP,
            ClientEvent(ack, self.id, event),
        )
        return ack

    def fetch_events(self) -> deque[TimedMessage]:
        return Network.receive(self.ip)

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
        last_t = perf_counter()
        clock = pygame.time.Clock()

        pygame.init()
        screen = pygame.display.set_mode((1000, 1000))
        while True:
            # init frame
            t = perf_counter()
            dt = t - last_t

            self.handle_events(self.fetch_events())

            input = self.get_input()
            ack = self.on_event(ClientInputEvent(input, dt))
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


@dataclass
class ClientInfo:
    ip: IpV4
    last_ack: Acknoledgement
    entity: ServerInputHandler
    events: EventBuffer[ServerSubEventType] = EventBuffer()


type ServerEntityType = ServerPlayerRobot | ServerEnemyRobot


class Server:
    clients: dict[ClientId, ClientInfo] = {}
    ip: IpV4
    receiver: Receiver

    entities: dict[EntityId, ServerEntityType]

    def __init__(self, ip: IpV4) -> None:
        self.ip = ip
        self.receiver = Receiver(self.ip)

        enemy_id = 0
        enemy = ServerEnemyRobot(
            (Vector2(10, 1), Vector2(1, 0)),
            pygame.Color(255, 0, 0),
            self.on_event_factory(None, enemy_id),
        )
        self.entities = {enemy_id: enemy}

        self.loop()

    def on_event_factory(
        self, client: Optional[ClientId], entity: EntityId
    ) -> OnEvent[object]:
        SEE = ServerEntityEvent
        return lambda n, e: self.on_event(client, f"{entity}/{n}", SEE(entity, n, e))

    def on_event(
        self,
        client: Optional[ClientId],
        event_name: EventName,
        event: ServerSubEventType,
    ):
        targets_ids = [client] if client is not None else self.clients.keys()
        for target_id in targets_ids:
            target = self.clients[target_id]
            target.events.dispatch(event_name, event)

    def handle_messages(self, messages: Sequence[TimedMessage]) -> None:
        for _, msg in messages:
            if not isinstance(msg, ClientEvent):
                raise ValueError("handle_messages: not ClientEvent")
            if isinstance(msg.event, ClientConnectionRequestEvent):
                client_id = gen_id(self.clients.keys())
                entity_id, entity = self.gen_client_entity(client_id)
                self.entities[entity_id] = entity
                client = ClientInfo(msg.event.ip, msg.ack, entity)
                self.clients[client_id] = client
                self.on_event(
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
            pygame.Color(0, 255, 0),
            self.on_event_factory(None, entity_id),
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

                self.handle_messages(self.receiver.received_until(t_frame))

                for entity in self.entities.values():
                    entity.tick(dt_frame, t_frame)

            # # rendering
            # pygame.event.pump()
            # screen.fill("black")
            # self.render(screen, self.entities.values())
            # pygame.display.flip()
            # print("rendered")

            # send events to clients
            for client in self.clients.values():
                for evt in client.events.collect():
                    Network.send(client.ip, ServerEvent(client.last_ack, evt))

            # cleanup udpate
            last_t = t_update
            clock.tick(1 / SERVER_TIMESTEP)


Thread(target=Server, args=(SERVER_IP,)).start()
client = Client(1234)
