from functools import cache
from typing import TYPE_CHECKING

import pygame

from roboarena.client.menu.renderable import Renderable
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.util import graphic_path
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


@cache
def get_default_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(graphic_path("font/ka1.ttf"), size)


class Text(Renderable):
    content: str
    size: int

    def __init__(self, content: str, size: int, position_pct: Vector[int]) -> None:
        font = get_default_font(size)
        texture = font.render(content, True, (0, 0, 0))
        texture_size = size_from_texture_width(texture, width=15)
        super().__init__(position_pct, texture, texture_size)
        self.content = content
        self.size = size

    def render(self, ctx: "RenderCtx") -> None:
        super().render(ctx)
