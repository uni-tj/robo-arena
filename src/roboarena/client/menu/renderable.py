from abc import ABC
from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.render_ctx import RenderCtx


class Renderable(ABC):
    dimensions_px: Vector[float] = Vector(0, 0)
    position_pct: Vector[int]
    position_px: Vector[float] = Vector(0, 0)
    texture: Surface

    def __init__(self, position_pct: Vector[int], texture: Surface) -> None:
        self.position_pct = position_pct
        self.texture = texture

    def render(self, ctx: "RenderCtx") -> None:
        self.update_dimensions(ctx.scale_texture(self.texture))
        self.update_position(ctx)
        ctx.screen.blit(ctx.scale_texture(self.texture), self.position_px.tuple_repr())

    def update_position(self, ctx: "RenderCtx") -> None:
        self.position_px = (
            ctx.screen_dimenions_px * self.position_pct / 100
        ) - self.dimensions_px / 2

    def update_dimensions(self, texture: Surface) -> None:
        self.dimensions_px = Vector.from_tuple(texture.get_size())
