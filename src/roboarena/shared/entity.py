import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from pygame import Surface

from roboarena.shared.constants import PlayerConstants
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion, Position
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.game import GameState
    from roboarena.shared.rendering.renderer import RenderCtx

logger = logging.getLogger(f"{__name__}")


class Value[T](ABC):

    @abstractmethod
    def get(self) -> T: ...


class Collidable(ABC):
    @property
    @abstractmethod
    def hitbox(self) -> Rect: ...


class CollideAroundCenter(Collidable):
    "Hitbox is centered around the current center"

    _center: Callable[[], Vector[float]]
    _rect: Rect

    def __init__(self, center: Callable[[], Vector[float]], rect: Rect) -> None:
        self._center = center
        self._rect = rect

    @property
    def hitbox(self) -> Rect:
        return self._rect.centerAround(self._center())


class Entity(ABC):
    _game: "GameState"
    collision: Collidable
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
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    texture = playerRobotTexture
    texture_size = size_from_texture_width(playerRobotTexture, width=1.0)

    def __init__(self, game: "GameState") -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self.motion.get()[0], Rect.from_width_height(Vector.one())
        )

    @property
    def position(self) -> Position:
        return self.motion.get()[0]

    def move(self, current: Motion, ctx: PlayerRobotMoveCtx) -> Motion:
        input, dt = ctx
        cur_position, cur_orientation = current

        new_orientation = Vector[float](0.0, 0.0)
        if input.move_right:
            new_orientation += Vector(PlayerConstants.ACCELEARTE, 0.0)
        if input.move_down:
            new_orientation += Vector(0.0, PlayerConstants.ACCELEARTE)
        if input.move_left:
            new_orientation += Vector(-PlayerConstants.ACCELEARTE, 0.0)
        if input.move_up:
            new_orientation += Vector(0.0, -PlayerConstants.ACCELEARTE)
        if new_orientation.length() != 0.0:
            new_orientation = new_orientation.normalize()
            new_orientation = new_orientation + cur_orientation
        else:
            new_orientation = cur_orientation * PlayerConstants.DECELERATE

        if new_orientation.length() > PlayerConstants.MAX_SPEED:
            new_orientation = new_orientation.normalize()
            new_orientation *= PlayerConstants.MAX_SPEED

        if new_orientation.length() < 0.1:
            new_orientation = Vector(0.0, 0.0)

        new_position = cur_position + new_orientation * dt

        return (new_position, new_orientation)


playerBulletTexture = Surface((10, 10))
playerBulletTexture.fill((50, 168, 82))  # dark green

type PlayerBulletMoveCtx = tuple[Time]


class PlayerBullet(Entity):
    texture = playerBulletTexture
    texture_size = Vector(0.2, 0.2)
    _position: Value[Vector[float]]
    "In units/second"
    _velocity: Value[Vector[float]]

    def __init__(self, game: "GameState") -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self._position.get(), Rect.from_width_height(Vector.one())
        )

    @property
    def position(self) -> Position:
        return self._position.get()

    def move(self, position: Vector[float], dt: Time, ctx: None) -> Vector[float]:
        return position + self._velocity.get() * dt


type EnemyRobotMoveCtx = tuple[Time]

enemyRobotTexture = Surface((50, 50))
enemyRobotTexture.fill("red")


class EnemyRobot(Entity):
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    texture = enemyRobotTexture
    texture_size = size_from_texture_width(playerRobotTexture, width=1.0)
    initial_position: Position

    def __init__(self, game: "GameState", motion: Motion) -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self.motion.get()[0], Rect.from_width_height(Vector.one())
        )
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
