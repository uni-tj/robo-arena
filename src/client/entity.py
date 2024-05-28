from typing import Callable
from abc import ABC, abstractmethod
from bisect import insort_right
from collections import deque
from pygame import Vector2, Color

from shared.types import Input, Motion, Acknoledgement
from shared.time import Time
from shared.constants import SERVER_TIMESTEP
from shared.entity import (
    Value,
    PlayerRobotMoveCtx,
    PlayerRobot,
    EnemyRobot,
    Entity,
    interpolateMotion,
)
from server.events import EventName


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


# class ExtrapolatedValue[T](UpdatableValue[T], ABC):
#     last_snapshot: tuple[Time, T]
#     _value: T

#     def __init__(self, value: T, t: Time) -> None:
#         super().__init__()
#         self.last_snapshot = (t, value)

#     @abstractmethod
#     def extrapolate(self, value: T, dt: Time) -> T: ...

#     def tick_client(self, input: Input, dt: Time, t: Time) -> None:
#         self._value = self.extrapolate(self.last_snapshot[1], self.last_snapshot[0])

#     def on_server_update(
#         self, value: T,
#         last_ack: Acknoledgement,
#         t_ack: Time
#     ) -> None:
#         self.last_snapshot = (t_ack, value)

#     @property
#     def value(self) -> T:
#         return self._value


class PassiveRemoteValue[T](Value[T]):
    value: T

    def __init__(self, value: T) -> None:
        super().__init__()
        self.value = value

    def on_server(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


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


type ClientEntityType = ClientPlayerRobot | ClientEnemyRobot


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
