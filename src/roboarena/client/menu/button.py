from typing import TYPE_CHECKING, Callable, Tuple

from pygame import Surface

from roboarena.client.menu.renderable import Renderable
from roboarena.shared.rendering.util import size_from_texture_height
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Button(Renderable):
    texture_uh: Surface
    texture_h: Surface
    texture_size: Vector[float]
    function: Callable[[], None]

    def __init__(
        self,
        texture_uh: Surface,
        texture_h: Surface,
        position_pct: Vector[int],
        function: Callable[[], None],
    ) -> None:
        texture_size = size_from_texture_height(texture_uh, height=1.3)
        super().__init__(position_pct, texture_uh, texture_size)
        self.texture_uh = texture_uh
        self.texture_h = texture_h
        self.function = function

    def mouse_over(self, mouse_pos_px: Tuple[int, int]) -> bool:
        return (
            self.position_px.x
            <= mouse_pos_px[0]
            <= self.position_px.x + self.dimensions_px.x
            and self.position_px.y
            <= mouse_pos_px[1]
            <= self.position_px.y + self.dimensions_px.y
        )

    def render(self, ctx: "RenderCtx") -> None:
        super().render(ctx)

    def handle_mouse_pos(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            self.texture = self.texture_h
        else:
            self.texture = self.texture_uh

    def handle_mouse_click(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            self.function()
