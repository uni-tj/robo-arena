from abc import ABC
from dataclasses import dataclass
from typing import TypeVar

from roboarena.utils.vector import Vector
from pygame import Surface
from pygame.transform import scale

"""
Two different coordinate systems that are not static
- Level coordinates (Absolut against the level origin)
- Player coordinates (Absolut against the player position
in the Level coordinate system)
50x65 texture
"""

N = TypeVar("N", float, int)


@dataclass(frozen=True)
class RenderingCtx:
    screen: Surface
    screen_dimenions: Vector[float]
    camera_position: Vector[float]
    px_per_gu: float


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface
    collision: bool

    def render(self, position: Vector[float], ctx: RenderingCtx) -> None: ...


class FloorBlock:
    texture: Surface
    collision = False

    def render(self, position: Vector[float], ctx: RenderingCtx):
        scaled_texture = scale(
            self.texture, vec_gu2px(Vector(1, 1), ctx).vector2_repr()
        )
        ctx.screen.blit(scaled_texture, gu2screen(position, ctx).vector2_repr())


class WallBlock:
    texture: Surface
    collision = True

    def render(self, position: Vector[float], ctx: RenderingCtx):
        scaled_texture = scale(
            self.texture, vec_gu2px(Vector(1, 1), ctx).vector2_repr()
        )
        ctx.screen.blit(
            scaled_texture,
            (gu2screen(position, ctx) - vec_gu2px(Vector(0, 0.2), ctx)).vector2_repr(),
        )


def gu2screen(gu: Vector[float], ctx: RenderingCtx) -> Vector[float]:
    return vec_gu2px(gu - ctx.camera_position, ctx) + ctx.screen_dimenions * Vector(
        0.5, 0.5
    )


def gu2px(gu: float, ctx: RenderingCtx) -> float:
    return gu * ctx.px_per_gu


def vec_gu2px[T: int | float](gu: Vector[T], ctx: RenderingCtx) -> Vector[T]:
    return gu * Vector(ctx.px_per_gu, ctx.px_per_gu)
