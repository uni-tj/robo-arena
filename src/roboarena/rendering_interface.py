from abc import ABC
from dataclasses import dataclass
from roboarena.utils.vector import Vector
from pygame import Surface
from pathlib import Path


@dataclass(frozen=True)
class BlockCtx(ABC):
    graphics_path: Path
    collision: bool


@dataclass(frozen=True)
class RenderingCtx:
    screen: Surface
    screen_dimenions_px: Vector[int]
    camera_position_gu: Vector[float]
    px_per_gu: float


# @dataclass(frozen=True)
# class Block:
#     texture: Surface
#     height_gu: int

#     def render_block(self, screen: Surface, block_pos: Vector[int]): ...


type Rect = tuple[int, int]


class Entity(ABC):
    texture: Surface
    texture_rect = Rect
    position: Vector[float]


type Level = dict[Vector[int], Block]
type EntityId = int
type Entities = dict[EntityId, Entity]


"""
Two different coordinate systems that are not static
- Level coordinates (Absolut against the level origin)
- Player coordinates (Absolut against the player position in the Level coordinate
system)
50x65 texture
"""


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface
    collision: bool

    def render(self, position: Vector[float], ctx: RenderingCtx) -> None: ...


class FloorBlock:
    texture: Surface
    collision: bool = False

    # def render(self, position: Vector[float], ctx: RenderingCtx):
    #     scaled_texture = scale(
    #         self.texture, vec_gu2px(Vector(1, 1), ctx).vector2_repr()
    #     )
    #     ctx.screen.blit(scaled_texture, gu2screen(position, ctx).vector2_repr())


class WallBlock:
    texture: Surface
    collision = True

    # def render(self, position: Vector[float], ctx: RenderingCtx):
    #     scaled_texture = scale(
    #         self.texture, vec_gu2px(Vector(1, 1), ctx).vector2_repr()
    #     )
    #     ctx.screen.blit(
    #         scaled_texture,
    #         (gu2screen(position, ctx) -
    # (vec_gu2px(Vector(0, 0.2), ctx)).vector2_repr()),
    #     )


# def gu2screen(gu: Vector[float], ctx: RenderingCtx) -> Vector[float]:
#     return (vec_gu2px(gu - ctx.camera_position_gu, ctx) + ctx.screen_dimenions
# * Vector(
#         0.5,[] 0.5
#     ))


# def gu2px(gu: float, ctx: RenderingCtx) -> float:
#     return gu * ctx.px_per_gu


# def vec_gu2px[T: int | float](gu: Vector[T], ctx: RenderingCtx) -> Vector[T]:
#     return gu * Vector(ctx.px_per_gu, ctx.px_per_gu)
