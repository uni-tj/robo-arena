import logging
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable
from itertools import chain
from math import copysign, degrees
from typing import TYPE_CHECKING, Callable

import pygame
from attrs import define, field
from pygame import Surface

from roboarena.shared.constants import PlayerConstants
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion, Position, Weapon
from roboarena.shared.util import load_graphic, rotate
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

    def prepare_render(self, ctx: "RenderCtx") -> Iterable["RenderInfo"]:
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        # Simulate physically square base surface by offsetting
        # by half width to bottom
        bottom_right_gu = self.position + (self.texture_size.x / 2)
        top_left_gu = bottom_right_gu - self.texture_size
        yield scaled_texture, ctx.gu2screen(top_left_gu).to_tuple()

    @abstractmethod
    def tick(self, dt: Time, t: Time): ...


bullet_texture_friendly = load_graphic("bullets/bullet-player.png")
bullet_texture_unfriendly = load_graphic("bullets/bullet-enemy.png")
bullet_texture_size = Vector.one()  # * 9 / 50

type BulletMoveCtx = tuple[Time]


class Bullet(Entity):
    texture_size = bullet_texture_size
    friendly: bool
    blocks_robot = False
    blocks_bullet = False
    _position: Value[Vector[float]]
    _velocity: Value[Vector[float]]
    "In units/second"

    def __init__(self, game: "GameState", friendly: bool) -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self._position.get(),
            Rect.from_width_height(bullet_texture_size),
        )
        self.texture = (
            bullet_texture_friendly if friendly else bullet_texture_unfriendly
        )
        self.friendly = friendly

    @property
    def position(self) -> Position:
        return self._position.get()

    def move(self, position: Vector[float], dt: Time, ctx: None) -> Vector[float]:
        return position + self._velocity.get() * dt


@define
class SharedWeapon:
    texture: Surface = field(default=load_graphic("weapons/laser-gun.PNG"), init=False)
    texture_size: Vector[float] = field(
        default=size_from_texture_width(
            load_graphic("weapons/laser-gun.PNG"), width=0.75
        ),
        init=False,
    )
    _game: "GameState"
    _entity: Entity
    _weapon: Weapon
    _aim: Callable[[], Position]

    def prepare_render(self, ctx: "RenderCtx") -> Iterable["RenderInfo"]:
        angle = degrees(Vector.angle(self._aim() - self._entity.position, Vector(1, 0)))
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        rotated_texture = rotate(
            scaled_texture,
            (90 - abs(abs(angle) - 90)) * copysign(1, angle),
            (0, scaled_texture.get_height() // 2),
        )
        flipped_texture = (
            pygame.transform.flip(rotated_texture, flip_x=True, flip_y=False)
            if abs(angle) > 90
            else rotated_texture
        )
        pos_screen = (
            ctx.gu2screen(self._entity.position)
            - Vector.from_tuple(rotated_texture.get_size()) // 2
        )
        yield flipped_texture, pos_screen.to_tuple()


type PlayerRobotMoveCtx = tuple[Input, Time]


def interpolateMotion(old: Motion, new: Motion, blend: float, ctx: None) -> Motion:
    return (
        old[0] + (new[0] - old[0]) * blend,
        old[1] + (new[1] - old[1]) * blend,
    )


PLAYER_CENTRE_TEXTURE = load_graphic("player/player-centre.png")
PLAYER_LEFT_TEXTURE = load_graphic("player/player-left.png")
PLAYER_LEFT_HALF_TEXTURE = load_graphic("player/player-left-half.png")
PLAYER_RIGHT_TEXTURE = load_graphic("player/player-right.png")
PLAYER_RIGHT_HALF_TEXTURE = load_graphic("player/player-right-half.png")


class PlayerRobot(Entity):
    _logger = logging.getLogger(f"{__name__}.PlayerRobot")
    collision: CollideAroundCenter
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    weapon: SharedWeapon
    texture = PLAYER_CENTRE_TEXTURE
    texture_size = size_from_texture_width(PLAYER_CENTRE_TEXTURE, width=1.0)
    _texture_queue: deque[Surface]
    blocks_robot = False
    blocks_bullet = False

    def __init__(self, game: "GameState") -> None:
        super().__init__(game)
        self._texture_queue = deque()
        self._texture_queue.extend([PLAYER_CENTRE_TEXTURE] * 7)
        self.collision = CollideAroundCenter(  # type: ignore
            lambda: self.motion.get()[0], Rect.from_size(Vector.from_scalar(0.95))
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

    def prepare_render(self, ctx: "RenderCtx") -> Iterable["RenderInfo"]:
        self.texture = self._texture_queue.popleft()
        _, orientation = self.motion.get()
        if len(self._texture_queue) == 0:
            if orientation.x > 0.5 or orientation.y < -0.5:
                self._texture_queue.extend([PLAYER_RIGHT_HALF_TEXTURE] * 7)
                self._texture_queue.extend([PLAYER_RIGHT_TEXTURE] * 7)
                self._texture_queue.extend([PLAYER_CENTRE_TEXTURE] * 7)
            elif orientation.x < -0.5 or orientation.y > 0.5:
                self._texture_queue.extend([PLAYER_LEFT_HALF_TEXTURE] * 7)
                self._texture_queue.extend([PLAYER_LEFT_TEXTURE] * 7)
                self._texture_queue.extend([PLAYER_CENTRE_TEXTURE] * 7)
            else:
                self._texture_queue.extend([PLAYER_CENTRE_TEXTURE] * 7)

        return chain(super().prepare_render(ctx), self.weapon.prepare_render(ctx))


type EnemyRobotMoveCtx = tuple[Time]

enemy_robot_texture = Surface((50, 50))
enemy_robot_texture.fill("red")


ENEMY_TEXTURE_1 = load_graphic("enemy/enemy-1.png")
ENEMY_TEXTURE_2 = load_graphic("enemy/enemy-2.png")
ENEMY_TEXTURE_3 = load_graphic("enemy/enemy-3.png")


class EnemyRobot(Entity):
    health: Value[int]
    motion: Value[Motion]
    color: Value[Color]
    texture = ENEMY_TEXTURE_1
    texture_size = size_from_texture_width(ENEMY_TEXTURE_1, width=1.5)
    _texture_queue: deque[Surface]
    blocks_robot = False
    blocks_bullet = False
    initial_position: Position

    def __init__(self, game: "GameState", motion: Motion) -> None:
        super().__init__(game)
        self.collision = CollideAroundCenter(
            lambda: self.motion.get()[0], Rect.from_size(Vector.from_scalar(0.95))
        )
        self.initial_position = motion[0]
        self._texture_queue = deque()
        self._texture_queue.extend([ENEMY_TEXTURE_1] * 14)

    @property
    def position(self) -> Position:
        return self.motion.get()[0]

    def move(self, current: Motion, ctx: EnemyRobotMoveCtx) -> Motion:
        (dt,) = ctx
        pos, ori = current
        new_ori = ori * -1 if pos.distance_to(self.initial_position) > 3 else ori
        new_pos = pos + new_ori * dt
        return (new_pos, new_ori)

    def prepare_render(self, ctx: "RenderCtx") -> Iterable["RenderInfo"]:
        self.texture = self._texture_queue.popleft()
        if len(self._texture_queue) == 0:
            if self.texture == ENEMY_TEXTURE_1:
                self._texture_queue.extend([ENEMY_TEXTURE_2] * 14)
                self._texture_queue.extend([ENEMY_TEXTURE_3] * 14)
            elif self.texture == ENEMY_TEXTURE_3:
                self._texture_queue.extend([ENEMY_TEXTURE_2] * 14)
                self._texture_queue.extend([ENEMY_TEXTURE_1] * 14)
        return super().prepare_render(ctx)


class DoorEntity(Entity):
    OPEN_TEXTURE = Surface((50, 65), pygame.SRCALPHA)
    CLOSED_TEXTURE = load_graphic("doors/door-closed.png")

    @property
    def texture(self) -> Surface:  # type: ignore
        if self.open.get():
            return self.OPEN_TEXTURE
        return self.CLOSED_TEXTURE

    texture_size: Vector[float] = size_from_texture_width(OPEN_TEXTURE, width=1.0)

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
