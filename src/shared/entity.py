from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame
from pygame import Rect, Surface, Vector2

from shared.rendering import px
from shared.time import Time
from shared.types import Color, Input, Motion, Position

if TYPE_CHECKING:
    from shared.game import GameState


class Value[T](ABC):

    @abstractmethod
    def get(self) -> T: ...


class Entity(ABC):
    _game: "GameState"
    hitbox: Rect

    def __init__(self, game: "GameState") -> None:
        super().__init__()
        self._game = game

    @abstractmethod
    def tick(self, dt: Time, t: Time): ...

    @abstractmethod
    def render(self, surface: Surface) -> None: ...


type PlayerRobotMoveCtx = tuple[Input, Time]


def interpolateMotion(old: Motion, new: Motion, blend: float, ctx: None) -> Motion:
    return (
        old[0] + (new[0] - old[0]) * blend,
        old[1] + (new[1] - old[1]) * blend,
    )


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
