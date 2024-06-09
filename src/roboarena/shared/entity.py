import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pygame import Rect, Surface

from roboarena.shared.rendering.render_ctx import FieldOfView, RenderingCtx
from roboarena.shared.time import Time
from roboarena.shared.types import Color, Input, Motion, Position
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.game import GameState

logger = logging.getLogger(f"{__name__}")


class Value[T](ABC):

    @abstractmethod
    def get(self) -> T: ...


class Entity(ABC):
    _game: "GameState"
    hitbox: Rect
    texture: Surface

    def __init__(self, game: "GameState") -> None:
        super().__init__()
        self._game = game

    @property
    @abstractmethod
    def position(self) -> Position: ...

    def visible_in_fov(self, fov: FieldOfView) -> bool:
        position = self.position
        return (
            position.x >= fov[0].x
            and position.x <= fov[1].x
            and position.y >= fov[0].y
            and position.y <= fov[1].y
        )

    def render(self, ctx: RenderingCtx) -> None:
        if not self.visible_in_fov(ctx.fov):
            return

        entity_pos_gu = self.position
        entity_dim_px = Vector.from_tuple(self.texture.get_size())
        entity_pos_px: Vector[float] = ctx.screen_dimenions_px * Vector(0.5, 0.5) - (
            ctx.camera_position_gu - entity_pos_gu
        ) * Vector(ctx.px_per_gu, ctx.px_per_gu)
        corrected_entity_pos_px: tuple[float, float] = ctx.scale_vector(
            entity_pos_px - entity_dim_px * 0.5
        ).tuple_repr()
        ctx.screen.blit(ctx.scale_texture(self.texture), corrected_entity_pos_px)

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
    motion: Value[Motion]
    color: Value[Color]
    texture = playerRobotTexture

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
