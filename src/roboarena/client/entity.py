import logging
from abc import ABC, abstractmethod
from bisect import insort_right
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import pygame
from attrs import define, field
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
from roboarena.shared.types import (
    Acknoledgement,
    DeathEvent,
    HitEvent,
    Input,
    Motion,
    Position,
    Weapon,
)
from roboarena.shared.util import EventTarget
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import GameState
    from roboarena.shared.rendering.renderer import RenderCtx


@dataclass(frozen=True)
class ChangedByInputEvent[T]:
    old: T
    new: T


@dataclass(frozen=True)
class ChangedByServerEvent[T]:
    old: T
    new: T


@dataclass(frozen=True)
class ChangedEvent[T]:
    old: T
    new: T


@define
class PredictedValue[T, Ctx](Value[T]):

    value: T
    predict: Callable[[T, Ctx], T]
    """Predict value using current and ctx"""
    events: EventTarget[
        ChangedByInputEvent[T] | ChangedByServerEvent[T] | ChangedEvent[T]
    ] = field(factory=EventTarget)
    _predicted_inputs: deque[tuple[Acknoledgement, Ctx]] = deque()
    """Queue of ack and ctx"""

    def on_input(
        self,
        ctx: Ctx,
        ack: Acknoledgement,
    ) -> None:
        old_value = self.value
        self._predicted_inputs.append((ack, ctx))
        self.value = self.predict(self.value, ctx)
        if self.value != old_value:
            self.events.dispatch(ChangedByInputEvent(old_value, self.value))
            self.events.dispatch(ChangedEvent(old_value, self.value))

    def on_server(self, value: T, last_ack: Acknoledgement) -> None:
        old_value = self.value
        self.value = value
        while (
            len(self._predicted_inputs) > 0 and self._predicted_inputs[0][0] <= last_ack
        ):
            # already respected by server snapshot, so remove
            self._predicted_inputs.popleft()
        for _, ctx in self._predicted_inputs:
            self.value = self.predict(self.value, ctx)
        if self.value != old_value:
            self.events.dispatch(ChangedByServerEvent(old_value, self.value))
            self.events.dispatch(ChangedEvent(old_value, self.value))

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


@define
class PassiveRemoteValue[T](Value[T]):
    value: T
    events: EventTarget[ChangedByServerEvent[T] | ChangedEvent[T]] = field(
        factory=EventTarget, init=False
    )

    def on_server(self, value: T) -> None:
        old_value = self.value
        self.value = value
        if self.value != old_value:
            self.events.dispatch(ChangedByServerEvent(old_value, self.value))
            self.events.dispatch(ChangedEvent(old_value, self.value))

    def get(self) -> T:
        return self.value


class ClientInputHandler(Entity, ABC):
    @abstractmethod
    def on_input(self, input: Input, dt: Time, ack: Acknoledgement, t: Time): ...


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


class ShotEvent:
    """Fired after shooting"""


@define
class ClientWeapon:
    _game: "GameState"
    _entity: ClientEntityType
    events: EventTarget[ShotEvent] = field(factory=EventTarget, init=False)

    _weapon: Weapon
    _last_shot: float = field(default=0.0, init=False)
    """
    The time the last shot was fired.

    Not kept in sync with the server, as it is reset reguarly, i.e. as soon as the
    the player stops shooting longer than the weapon cooldown.
    """

    def on_input(self, input: Input, t: Time):
        if not input.primary:
            return
        if t - self._last_shot < self._weapon.wepaon_cooldown:
            return
        self._last_shot = t
        self.shoot()

    def on_server(self, weapon: Weapon):
        self._weapon = weapon
        self._last_shot = 0.0

    def shoot(self):
        self.events.dispatch(ShotEvent())


@dataclass(frozen=True)
class MovedEvent:
    pass


class ClientPlayerRobot(PlayerRobot, ClientEntity, ClientInputHandler):
    health: PassiveRemoteValue[int]
    motion: PredictedValue[Motion, PlayerRobotMoveCtx]
    color: PassiveRemoteValue[Color]
    weapon: ClientWeapon
    aim: Position
    events: EventTarget[MovedEvent | HitEvent | DeathEvent]

    def __init__(
        self,
        game: "GameState",
        health: int,
        motion: Motion,
        color: Color,
        weapon: Weapon,
    ) -> None:
        super().__init__(game)
        self.health = PassiveRemoteValue(health)  # type: ignore
        self.motion = PredictedValue(motion, self.move)  # type: ignore
        self.color = PassiveRemoteValue(color)  # type: ignore
        self.weapon = ClientWeapon(game, self, weapon)
        self.aim = Vector(0, 0)
        self.events = EventTarget()

        dispatch = self.events.dispatch
        self.health.events.add_listener(
            ChangedByServerEvent,
            lambda e: dispatch(HitEvent()) if e.old > e.new else None,  # type: ignore
        )
        self.health.events.add_listener(
            ChangedByServerEvent,
            lambda e: dispatch(DeathEvent()) if e.new <= 0 else None,  # type: ignore
        )
        self.motion.events.add_listener(
            ChangedByInputEvent,
            lambda e: (dispatch(MovedEvent()) if e.old[0] != e.new[1] else None),  # type: ignore
        )

    def on_input(self, input: Input, dt: Time, ack: Acknoledgement, t: Time):
        self.motion.on_input((input, dt), ack)
        self.weapon.on_input(input, t)
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
            case "weapon", Weapon():
                self.weapon.on_server(event)
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
    weapon: ClientWeapon
    events: EventTarget[HitEvent | DeathEvent]

    def __init__(
        self,
        game: "GameState",
        health: int,
        motion: Motion,
        color: Color,
        weapon: Weapon,
        last_ack: Acknoledgement,
        t_ack: Time,
    ) -> None:
        super().__init__(game, motion)
        self.health = PassiveRemoteValue(health)  # type: ignore
        self.motion = InterpolatedValue(motion, last_ack, t_ack, interpolateMotion)  # type: ignore
        self.color = PassiveRemoteValue(color)  # type: ignore
        self.weapon = ClientWeapon(game, self, weapon)
        self.events = EventTarget()

        dispatch = self.events.dispatch
        self.health.events.add_listener(
            ChangedByServerEvent,
            lambda e: dispatch(HitEvent()) if e.old > e.new else None,  # type: ignore
        )
        self.health.events.add_listener(
            ChangedByServerEvent,
            lambda e: dispatch(DeathEvent()) if e.new <= 0 else None,  # type: ignore
        )

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
            case "weapon", Weapon():
                self.weapon.on_server(event)
            case n, e:
                raise ValueError(f"entity: invalid event {n}={e}")

    def tick(self, dt: Time, t: Time):
        self.motion.tick(t, None)
