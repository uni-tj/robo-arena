from abc import ABC, abstractmethod
from functools import partial
from typing import TYPE_CHECKING, Callable

from roboarena.server.events import Dispatch, SimpleDispatch
from roboarena.shared.entity import (
    EnemyRobot,
    EnemyRobotMoveCtx,
    Entity,
    PlayerRobot,
    PlayerRobotMoveCtx,
    Value,
)
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion

if TYPE_CHECKING:
    from roboarena.server.server import GameState


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
    def on_input(self, input: Input, dt: Time): ...


type ServerEntityType = ServerPlayerRobot | ServerEnemyRobot


class ServerPlayerRobot(PlayerRobot, ServerInputHandler):
    motion: CalculatedValue[Motion, PlayerRobotMoveCtx]
    color: ActiveRemoteValue[Color]

    def __init__(
        self,
        game: "GameState",
        motion: Motion,
        color: Color,
        dispatch: Dispatch[Motion | Color],
    ) -> None:
        super().__init__(game)
        self.motion = CalculatedValue(motion, self.move, partial(dispatch, "motion"))  # type: ignore
        self.color = ActiveRemoteValue(color, partial(dispatch, "color"))  # type: ignore

    def on_input(self, input: Input, dt: Time):
        self.motion.tick((input, dt))

    def tick(self, dt: Time, t: Time):
        pass


class ServerEnemyRobot(EnemyRobot):
    motion: CalculatedValue[Motion, EnemyRobotMoveCtx]
    color: ActiveRemoteValue[Color]

    def __init__(
        self,
        game: "GameState",
        motion: Motion,
        color: Color,
        dispatch: Dispatch[Motion | Color],
    ) -> None:
        super().__init__(game, motion)
        self.motion = CalculatedValue(  # type: ignore
            motion, self.move, partial(dispatch, "motion")
        )
        self.color = ActiveRemoteValue(color, partial(dispatch, "color"))  # type: ignore

    def tick(self, dt: Time, t: Time):
        self.motion.tick((dt,))
