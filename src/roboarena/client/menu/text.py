from typing import TYPE_CHECKING

import pygame

from roboarena.client.menu.renderable import Renderable
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Text(Renderable):
    content: str
    size: int

    def __init__(self, content: str, size: int, position_pct: Vector[int]) -> None:
        self.content = content
        self.size = size
        font = pygame.font.Font(None, size)
        texture = font.render(content, True, (255, 255, 255))

        super().__init__(position_pct, texture)

    def render_text(self, ctx: "RenderCtx") -> None:
        super().render(ctx)
