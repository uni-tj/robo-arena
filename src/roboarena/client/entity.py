import logging
from abc import ABC, abstractmethod
from bisect import insort_right
from collections import deque
from typing import TYPE_CHECKING, Callable

import pygame
from pygame import Color

from roboarena.server.events import EventName
from roboarena.shared.constants import SERVER_TIMESTEP
from roboarena.shared.entity import (
    EnemyRobot,
    Entity,
    PlayerBullet,
    PlayerRobot,
    PlayerRobotMoveCtx,
    Value,
    interpolateMotion,
)
from roboarena.shared.time import Time
from roboarena.shared.types import Acknoledgement, Input, Motion, Position
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import GameState
    from roboarena.shared.rendering.renderer import RenderCtx


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
    _logger = logging.getLogger(f"{__name__}.InterpolatedValue")
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
        # display current value until a future value has buffered
        self.snapshots = deque(
            [(last_ack, t - SERVER_TIMESTEP, value), (last_ack, t, value)]
        )

    def tick(self, t: Time, ctx: Ctx) -> None:
        interpolated_t = t - SERVER_TIMESTEP

        # delete old snapshots
        # snapshots of the current frame trated as old snapshots bc easier interpolation
        while len(self.snapshots) >= 2 and self.snapshots[1][1] <= interpolated_t:
            self.snapshots.popleft()
        if self.snapshots[0][1] > interpolated_t:
            # only future snapshot available
            # this should not happen, since __init__ adds old snapshot
            self._logger.error(f"only future snapshot: {self.snapshots}")
            raise ValueError(f"only future snapshot: {self.snapshots}")

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


class ExtrapolatedValue[T, Ctx](Value[T]):
    _last_snapshot: tuple[Acknoledgement, Time, T]
    _extrapolate: Callable[[T, Time, Ctx], T]
    _value: T

    def __init__(
        self,
        value: T,
        last_ack: Acknoledgement,
        t_ack: Time,
        extrapolate: Callable[[T, Time, Ctx], T],
    ) -> None:
        super().__init__()
        self._last_snapshot = (last_ack, t_ack, value)
        self._extrapolate = extrapolate
        self._value = value

    def tick(self, t: Time, ctx: Ctx) -> None:
        dt = t - self._last_snapshot[1]
        self._value = self._extrapolate(self._last_snapshot[2], dt, ctx)

    def on_server(self, value: T, last_ack: Acknoledgement, t_ack: Time) -> None:
        if last_ack < self._last_snapshot[0]:
            return
        self._last_snapshot = (last_ack, t_ack, value)

    def get(self) -> T:
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


class ClientInputHandler(Entity, ABC):
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


type ClientEntityType = ClientPlayerRobot | ClientEnemyRobot | ClientPlayerBullet


class ClientPlayerRobot(PlayerRobot, ClientEntity, ClientInputHandler):
    health: PassiveRemoteValue[int]
    motion: PredictedValue[Motion, PlayerRobotMoveCtx]
    color: PassiveRemoteValue[Color]
    aim: Position

    def __init__(
        self, game: "GameState", health: int, motion: Motion, color: Color
    ) -> None:
        super().__init__(game)
        self.health = PassiveRemoteValue(health)  # type: ignore
        self.motion = PredictedValue(motion, self.move)  # type: ignore
        self.color = PassiveRemoteValue(color)  # type: ignore
        self.aim = Vector(0, 0)

    def on_input(self, input: Input, dt: Time, ack: Acknoledgement):
        self.motion.on_input((input, dt), ack)
        self.aim = input.mouse
        pass

    def on_server(
        self,
        event_name: EventName,
        event: object,
        last_ack: Acknoledgement,
        t_ack: Time,
    ):
        match event_name, event:
            case "motion", tuple(
                (Vector(float(), float()), Vector(float(), float())) as e  # type: ignore
            ):
                self.motion.on_server(e, last_ack)  # type: ignore
            case "color", Color():
                self.color.on_server(event)
            case "health", int():
                self.health.on_server(event)
            case n, e:
                raise ValueError(f"entity: invalid event {n}={e}")

    def tick(self, dt: Time, t: Time):
        pass

    def render(self, ctx: "RenderCtx") -> None:
        super().render(ctx)
        # render crosshair
        r = 10
        center = ctx.gu2screen(self.aim)
        pygame.draw.circle(ctx.screen, "orange", center.to_tuple(), r)


class ClientPlayerBullet(PlayerBullet, ClientEntity):
    _position: ExtrapolatedValue[Vector[float], None]
    _velocity: PassiveRemoteValue[Vector[float]]

    def __init__(
        self,
        game: "GameState",
        position: Vector[float],
        velocity: Vector[float],
        last_ack: Acknoledgement,
        t_ack: Time,
    ) -> None:
        super().__init__(game)
        self._position = ExtrapolatedValue(position, last_ack, t_ack, self.move)  # type: ignore
        self._velocity = PassiveRemoteValue(velocity)  # type: ignore

    def on_server(
        self,
        event_name: EventName,
        event: object,
        last_ack: Acknoledgement,
        t_ack: Time,
    ):
        match event_name, event:
            case "position", Vector(float(), float()):
                _event: Vector[float] = event
                self._position.on_server(_event, last_ack, t_ack)
            case "velocity", Vector(float(), float()):
                _event: Vector[float] = event
                self._velocity.on_server(_event)
            case _:
                raise ValueError("entity: invalid event")

    def tick(self, dt: Time, t: Time):
        self._position.tick(t, None)


class ClientEnemyRobot(EnemyRobot, ClientEntity):
    health: PassiveRemoteValue[int]
    motion: InterpolatedValue[Motion, None]
    color: PassiveRemoteValue[Color]

    def __init__(
        self,
        game: "GameState",
        health: int,
        motion: Motion,
        color: Color,
        last_ack: Acknoledgement,
        t_ack: Time,
    ) -> None:
        super().__init__(game, motion)
        self.health = PassiveRemoteValue(health)  # type: ignore
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
            case "motion", tuple(
                (Vector(float(), float()), Vector(float(), float())) as e  # type: ignore
            ):
                self.motion.on_server(e, last_ack, t_ack)  # type: ignore
            case "color", Color():
                self.color.on_server(event)
            case "health", int():
                self.health.on_server(event)
            case n, e:
                raise ValueError(f"entity: invalid event {n}={e}")

    def tick(self, dt: Time, t: Time):
        self.motion.tick(t, None)
