from abc import ABC
from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Renderable(ABC):
    position_pct: Vector[int]
    texture: Surface
    texture_size: Vector[float]
    position_px: Vector[float] = Vector(0, 0)
    dimensions_px: Vector[int] = Vector(0, 0)

    def __init__(
        self, position_pct: Vector[int], texture: Surface, texture_size: Vector[float]
    ) -> None:
        self.position_pct = position_pct
        self.texture = texture
        self.texture_size = texture_size

    def render(self, ctx: "RenderCtx") -> None:
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        self.update_dimensions(scaled_texture)
        self.update_position(ctx)
        ctx.screen.blit(scaled_texture, self.position_px.to_tuple())

    def update_position(self, ctx: "RenderCtx") -> None:
        self.position_px = ctx.pct2px(self.position_pct) - self.dimensions_px / 2

    def update_dimensions(self, texture: Surface) -> None:
        self.dimensions_px = Vector.from_tuple(texture.get_size())
