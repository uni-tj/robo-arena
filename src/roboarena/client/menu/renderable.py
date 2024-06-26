from abc import ABC
from functools import cached_property
from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.shared.rendering.util import size_from_texture
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Renderable(ABC):
    dimensions_px: Vector[float] = Vector(0, 0)
    position_pct: Vector[int]
    position_px: Vector[float] = Vector(0, 0)
    texture: Surface

    def __init__(self, position_pct: Vector[int], texture: Surface) -> None:
        self.position_pct = position_pct
        self.texture = texture

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture(self.texture, width=1.5)

    def render(self, ctx: "RenderCtx") -> None:
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        self.update_dimensions(scaled_texture)
        self.update_position(ctx)
        ctx.screen.blit(scaled_texture, self.position_px.to_tuple())

    def update_position(self, ctx: "RenderCtx") -> None:
        self.position_px = ctx.pct2px(self.position_pct) - self.dimensions_px / 2

    def update_dimensions(self, texture: Surface) -> None:
        self.dimensions_px = Vector.from_tuple(texture.get_size())
