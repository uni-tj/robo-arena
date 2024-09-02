import logging
from abc import ABC, abstractmethod
from functools import cache
from typing import TYPE_CHECKING, Callable

import pygame
from attrs import define
from pygame import Surface

from roboarena.shared.constants import PlayerConstants
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion, Position
from roboarena.shared.util import load_graphic
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.game import GameState
    from roboarena.shared.rendering.renderer import RenderCtx, RenderInfo

logger = logging.getLogger(f"{__name__}")


class Value[T](ABC):

    @abstractmethod
    def get(self) -> T: ...


class Collidable(ABC):
    @property
    @abstractmethod
    def hitbox(self) -> Rect: ...


@define
class CollideAroundCenter(Collidable):
    "Hitbox is centered around a dynamic center"

    _center: Callable[[], Vector[float]]
    _rect: Rect

    @property
    def hitbox(self) -> Rect:
        return self._rect.centerAround(self._center())

    def hitbox_at(self, center: Vector[float]) -> Rect:
        return self._rect.centerAround(center)


class Entity(ABC):
    _game: "GameState"
    collision: Collidable
    texture: Surface
    """In gu"""
    texture_size: Vector[float]
    blocks_robot: bool
    blocks_bullet: bool

    def __init__(self, game: "GameState") -> None:
        super().__init__()
        self._game = game

    @property
    @abstractmethod
    def position(self) -> Position: ...

    def prepare_render(self, ctx: "RenderCtx") -> "RenderInfo":
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        # Simulate physically square base surface by offsetting
        # by half width to bottom
        bottom_right_gu = self.position + (self.texture_size.x / 2)
        top_left_gu = bottom_right_gu - self.texture_size
        return scaled_texture, ctx.gu2screen(top_left_gu).to_tuple()

    @abstractmethod
    def tick(self, dt: Time, t: Time): ...


type PlayerRobotMoveCtx = tuple[Input, Time]


def interpolateMotion(old: Motion, new: Motion, blend: float, ctx: None) -> Motion:
    return (
        old[0] + (new[0] - old[0]) * blend,
        old[1] + (new[1] - old[1]) * blend,
    )


player_robot_texture = Surface((50, 50))
player_robot_texture.fill("green")


class PlayerRobot(Entity):
    _logger = logging.getLogger(f"{__name__}.PlayerRobot")
    collision: CollideAroundCenter
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    texture = player_robot_texture
    texture_size = size_from_texture_width(player_robot_texture, width=1.0)
    blocks_robot = False
    blocks_bullet = False

    def __init__(self, game: "GameState") -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(  # type: ignore
            lambda: self.motion.get()[0], Rect.from_width_height(Vector.one())
        )

    @property
    def position(self) -> Position:
        return self.motion.get()[0]

    def move(self, current: Motion, ctx: PlayerRobotMoveCtx) -> Motion:
        input, dt = ctx
        cur_position, cur_velocity = current

        acceleration = Vector(0.0, 0.0)
        if input.move_right:
            acceleration += Vector(1, 0.0)
        if input.move_down:
            acceleration += Vector(0.0, 1)
        if input.move_left:
            acceleration += Vector(-1, 0.0)
        if input.move_up:
            acceleration += Vector(0.0, -1)
        if acceleration != Vector(0.0, 0.0):
            acceleration = acceleration.normalize() * PlayerConstants.ACCELEARTE

        new_velocity = cur_velocity * (1 - PlayerConstants.DECELERATE) + acceleration
        if new_velocity.length() < 0.1:
            new_velocity = Vector(0.0, 0.0)

        new_position = cur_position + new_velocity * dt
        if not self._game.blocking(self.collision.hitbox_at(new_position), "robot"):
            return (new_position, new_velocity)
        new_velocity_x = new_velocity * Vector(1, 0)
        new_position_x = cur_position + new_velocity_x * dt
        if not self._game.blocking(self.collision.hitbox_at(new_position_x), "robot"):
            return (new_position_x, new_velocity_x)
        new_velocity_y = new_velocity * Vector(0, 1)
        new_position_y = cur_position + new_velocity_y * dt
        if not self._game.blocking(self.collision.hitbox_at(new_position_y), "robot"):
            return (new_position_y, new_velocity_y)
        return (cur_position, Vector(0.0, 0.0))


player_bullet_texture = load_graphic("bullets/bullet-laser.png")
player_bullet_texture_size = Vector.one()  # * 9 / 50

type PlayerBulletMoveCtx = tuple[Time]


class PlayerBullet(Entity):
    texture = player_bullet_texture
    texture_size = player_bullet_texture_size
    blocks_robot = False
    blocks_bullet = False
    _position: Value[Vector[float]]
    _velocity: Value[Vector[float]]
    "In units/second"

    def __init__(self, game: "GameState") -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self._position.get(),
            Rect.from_width_height(player_bullet_texture_size),
        )

    @property
    def position(self) -> Position:
        return self._position.get()

    def move(self, position: Vector[float], dt: Time, ctx: None) -> Vector[float]:
        return position + self._velocity.get() * dt


type EnemyRobotMoveCtx = tuple[Time]

enemy_robot_texture = Surface((50, 50))
enemy_robot_texture.fill("red")


class EnemyRobot(Entity):
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    texture = enemy_robot_texture
    texture_size = size_from_texture_width(player_robot_texture, width=1.0)
    blocks_robot = False
    blocks_bullet = False
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


@cache
def load_door_texture_open() -> Surface:
    texture = Surface((50, 50))
    pygame.draw.rect(texture, (128, 128, 128), pygame.Rect((0, 20), (50, 10)))
    return texture


@cache
def load_door_texture_close() -> Surface:
    texture = Surface((50, 50))
    pygame.draw.rect(texture, (0, 0, 0), pygame.Rect((0, 20), (50, 10)))
    return texture


class DoorEntity(Entity):
    @property
    def texture(self) -> Surface:  # type: ignore
        if self.open.get():
            return load_door_texture_open()
        return load_door_texture_close()

    texture_size: Vector[float] = size_from_texture_width(
        load_door_texture_open(), width=1.0
    )

    @property
    def blocks_robot(self) -> bool:  # type: ignore
        return not self.open.get()

    blocks_bullet = True

    _position: Position
    open: Value[bool]

    def __init__(self, game: "GameState"):
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self.position, Rect.from_size(Vector.one())
        )

    @property
    def position(self) -> Position:
        return self._position
