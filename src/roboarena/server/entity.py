from abc import ABC, abstractmethod
from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable

from attrs import define, field

from roboarena.server.events import Dispatch, SimpleDispatch
from roboarena.shared.entity import (
    EnemyRobot,
    EnemyRobotMoveCtx,
    Entity,
    PlayerBullet,
    PlayerRobot,
    PlayerRobotMoveCtx,
    Value,
)
from roboarena.shared.time import Time
from roboarena.shared.types import (
    Color,
    EntityId,
    Input,
    Marker,
    Motion,
    PygameColor,
    ServerSpawnPlayerBulletEvent,
    ServerSpawnRobotEvent,
    Weapon,
    basic_weapon,
)
from roboarena.shared.util import EventTarget
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.server import GameState

logger = getLogger(__name__)


class ActiveRemoteValue[T](Value[T]):
    value: T
    dispatch: SimpleDispatch[T]

    def __init__(self, value: T, dispatch: SimpleDispatch[T]) -> None:
        self.value = value
        self.dispatch = dispatch

    def set(self, value: T) -> None:
        if value == self.value:
            return
        self.value = value
        self.dispatch(value)

    def get(self) -> T:
        return self.value


class CalculatedValue[T, Ctx](Value[T]):
    value: T
    calculate: Callable[[T, Ctx], T]
    dispatch: SimpleDispatch[T]

    def __init__(
        self,
        value: T,
        calculate: Callable[[T, Ctx], T],
        dispatch: SimpleDispatch[T],
    ) -> None:
        self.value = value
        self.calculate = calculate
        self.dispatch = dispatch

    def tick(self, ctx: Ctx) -> None:
        self.value = self.calculate(self.value, ctx)
        self.dispatch(self.value)

    def get(self) -> T:
        return self.value


class ServerInputHandler(Entity, ABC):
    @abstractmethod
    def on_input(self, input: Input, dt: Time, t: Time): ...


class HealthController(Value[int]):
    class DeathEvent:
        pass

    _health: int
    _dispatch: SimpleDispatch[int]
    events: EventTarget[DeathEvent]

    def __init__(self, health: int, dispatch: SimpleDispatch[int]) -> None:
        self._health = health
        self._dispatch = dispatch
        self.events = EventTarget()

    def hit(self, strength: int):
        self._health -= strength
        if self._health <= 0:
            self.events.dispatch(self.DeathEvent())
        self._dispatch(self._health)

    def get(self) -> int:
        return self._health


type ServerEntityType = ServerPlayerRobot | ServerEnemyRobot | ServerPlayerBullet


class ShotEvent:
    """Fired after shooting"""


@define
class ServerWeapon:
    _game: "GameState"
    _entity: ServerEntityType
    events: EventTarget[ShotEvent] = field(factory=EventTarget, init=False)

    _weapon: Weapon
    _last_shot: float = field(default=0.0, init=False)

    def on_input(self, input: Input, t: Time):
        if not input.primary:
            return
        if t - self._last_shot < self._weapon.wepaon_cooldown:
            return
        self._last_shot = t
        self.shoot(input.mouse - self._entity.position)

    def shoot(self, direction: Vector[float]):
        bullet = ServerPlayerBullet(
            self._game,
            self._entity.position,
            direction.normalize() * self._weapon.bullet_speed,
            self._weapon.bullet_strength,
        )
        self._game.create_entity(bullet)
        self.events.dispatch(ShotEvent())

    def get(self) -> Weapon:
        return self._weapon


class ServerPlayerRobot(PlayerRobot, ServerInputHandler):
    _game: "GameState"
    health: HealthController
    motion: CalculatedValue[Motion, PlayerRobotMoveCtx]
    color: ActiveRemoteValue[Color]
    weapon: ServerWeapon

    def __init__(
        self,
        game: "GameState",
        health: int,
        motion: Motion,
        color: Color,
        dispatch: Dispatch[Any],
    ) -> None:
        super().__init__(game)
        self._game = game  # type: ignore
        self.health = HealthController(health, partial(dispatch, "health"))  # type: ignore
        self.motion = CalculatedValue(motion, self.move, partial(dispatch, "motion"))  # type: ignore
        self.color = ActiveRemoteValue(color, partial(dispatch, "color"))  # type: ignore
        self.weapon = ServerWeapon(game, self, basic_weapon)

    def on_input(self, input: Input, dt: Time, t: Time):
        self.motion.tick((input, dt))
        self.weapon.on_input(input, t)

    def tick(self, dt: Time, t: Time):
        pass

    def to_event(self, entity_id: EntityId) -> ServerSpawnRobotEvent:
        return ServerSpawnRobotEvent(
            entity_id,
            self.health.get(),
            self.motion.get(),
            self.color.get(),
            self.weapon.get(),
        )


class ServerPlayerBullet(PlayerBullet):
    ServerPlayerBulletPositionCtx = tuple[Time]
    _game: "GameState"
    _position: CalculatedValue[Vector[float], ServerPlayerBulletPositionCtx]
    _velocity: ActiveRemoteValue[Vector[float]]
    _strength: int
    _hit_last_tick: set[Entity]

    def __init__(
        self,
        game: "GameState",
        position: Vector[float],
        velocity: Vector[float],
        strength: int,
    ) -> None:
        super().__init__(game)
        self._game = game  # type: ignore
        self._position = CalculatedValue(  # type: ignore
            position,
            lambda pos, ctx: self.move(pos, ctx[0], None),
            partial(self._game.dispatch, self, "position"),
        )
        self._velocity = ActiveRemoteValue(  # type: ignore
            velocity,
            partial(self._game.dispatch, self, "velocity"),
        )
        self._strength = strength

    def tick(self, dt: Time, t: Time):
        self._position.tick((dt,))
        if self._game.collidingWalls(self):
            self._game.mark(Marker(self.position, PygameColor.light_grey()))
            return self._game.delete_entity(self)

        hit_this_tick = set[Entity]()
        for entity in self._game.collidingEntities(self):
            self._game.mark(Marker(self.position, PygameColor.green()))
            if not isinstance(entity, ServerEnemyRobot):
                continue
            hit_this_tick.add(entity)
            if entity not in self._hit_last_tick:
                entity.health.hit(self._strength)
        self._hit_last_tick = hit_this_tick

    def to_event(self, entity_id: EntityId) -> ServerSpawnPlayerBulletEvent:
        return ServerSpawnPlayerBulletEvent(
            entity_id, self._position.get(), self._velocity.get()
        )


class ServerEnemyRobot(EnemyRobot):
    _game: "GameState"
    health: HealthController
    motion: CalculatedValue[Motion, EnemyRobotMoveCtx]
    color: ActiveRemoteValue[Color]
    weapon: ServerWeapon

    def __init__(
        self,
        game: "GameState",
        health: int,
        motion: Motion,
        color: Color,
        weapon: Weapon,
        dispatch: Dispatch[Motion | Color],
    ) -> None:
        super().__init__(game, motion)
        self._game = game  # type: ignore
        self.health = HealthController(health, partial(dispatch, "health"))  # type: ignore
        self.motion = CalculatedValue(  # type: ignore
            motion, self.move, partial(dispatch, "motion")
        )
        self.color = ActiveRemoteValue(color, partial(dispatch, "color"))  # type: ignore
        self.weapon = ServerWeapon(game, self, weapon)

        self.health.events.add_listener(
            self.health.DeathEvent, lambda e: self._game.delete_entity(self)
        )

    def tick(self, dt: Time, t: Time):
        self.motion.tick((dt,))

    def to_event(self, entity_id: EntityId) -> ServerSpawnRobotEvent:
        return ServerSpawnRobotEvent(
            entity_id,
            self.health.get(),
            self.motion.get(),
            self.color.get(),
            self.weapon.get(),
        )
