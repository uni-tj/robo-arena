import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pygame import Rect, Surface

from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion, Position
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.game import GameState
    from roboarena.shared.rendering.renderer import RenderCtx

logger = logging.getLogger(f"{__name__}")


class Value[T](ABC):

    @abstractmethod
    def get(self) -> T: ...


class Entity(ABC):
    _game: "GameState"
    hitbox: Rect
    texture: Surface
    """In gu"""
    texture_size: Vector[float]

    def __init__(self, game: "GameState") -> None:
        super().__init__()
        self._game = game

    @property
    @abstractmethod
    def position(self) -> Position: ...

    def render(self, ctx: "RenderCtx") -> None:
        if not ctx.fov.contains(self.position):
            return
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        # Simulate physically square base surface by offsetting
        # by half width to bottom
        bottom_right_gu = self.position + (self.texture_size.x / 2)
        top_left_gu = bottom_right_gu - self.texture_size
        ctx.screen.blit(scaled_texture, ctx.gu2screen(top_left_gu).to_tuple())

    @abstractmethod
    def tick(self, dt: Time, t: Time): ...


type PlayerRobotMoveCtx = tuple[Input, Time]


def interpolateMotion(old: Motion, new: Motion, blend: float, ctx: None) -> Motion:
    return (
        old[0] + (new[0] - old[0]) * blend,
        old[1] + (new[1] - old[1]) * blend,
    )


playerRobotTexture = Surface((50, 50))
playerRobotTexture.fill("green")


class PlayerRobot(Entity):
    _logger = logging.getLogger(f"{__name__}.PlayerRobot")
    motion: Value[Motion]
    color: Value[Color]
    texture = playerRobotTexture
    texture_size = size_from_texture_width(playerRobotTexture, width=1.0)

    @property
    def position(self) -> Position:
        return self.motion.get()[0]

    def move(self, current: Motion, ctx: PlayerRobotMoveCtx) -> Motion:
        input, dt = ctx
        cur_position, cur_orientation = current

        new_orientation = Vector[float](0.0, 0.0)
        if input.move_right:
            new_orientation += Vector(1.0, 0.0)
        if input.move_down:
            new_orientation += Vector(0.0, 1.0)
        if input.move_left:
            new_orientation += Vector(-1.0, 0.0)
        if input.move_up:
            new_orientation += Vector(0.0, -1.0)
        if new_orientation.length() != 0.0:
            new_orientation.normalize()

        new_position = cur_position + new_orientation * 5 * dt
        cached_orientation = (
            new_orientation
            if not (new_orientation == Vector(0.0, 0.0))
            else cur_orientation
        )
        return (new_position, cached_orientation)


type EnemyRobotMoveCtx = tuple[Time]

enemyRobotTexture = Surface((50, 50))
enemyRobotTexture.fill("red")


class EnemyRobot(Entity):
    motion: Value[Motion]
    color: Value[Color]
    texture = enemyRobotTexture
    texture_size = size_from_texture_width(playerRobotTexture, width=1.0)
    initial_position: Position

    def __init__(self, game: "GameState", motion: Motion) -> None:
        super().__init__(game)
        self.initial_position = motion[0]

    @property
    def position(self) -> Position:
        return self.motion.get()[0]

    def move(self, current: Motion, ctx: EnemyRobotMoveCtx) -> Motion:
        (dt,) = ctx
        pos, ori = current
        new_ori = ori * -1 if pos.distance_to(self.initial_position) > 3 else ori
        new_pos = pos + new_ori * dt
        return (new_pos, new_ori)
