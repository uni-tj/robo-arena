from typing import TYPE_CHECKING, Callable, Tuple

from pygame import Surface

from roboarena.client.menu.renderable import Renderable
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx


class Button(Renderable):
    texture_on_unhover: Surface
    texture_on_hover: Surface
    function: Callable[[], None]

    def __init__(
        self,
        texture_on_unhover: Surface,
        texture_on_hover: Surface,
        position_pct: Vector[int],
        function: Callable[[], None],
    ) -> None:
        self.texture_on_unhover = texture_on_unhover
        self.texture_on_hover = texture_on_hover
        self.function = function
        super().__init__(position_pct, texture_on_unhover)

    def mouse_over(self, mouse_pos_px: Tuple[int, int]) -> bool:
        return (
            self.position_px.x
            <= mouse_pos_px[0]
            <= self.position_px.x + self.dimensions_px.x
            and self.position_px.y
            <= mouse_pos_px[1]
            <= self.position_px.y + self.dimensions_px.y
        )

    def render_button(self, ctx: "RenderCtx") -> None:
        super().render(ctx)

    def handle_mouse_pos(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            self.texture = self.texture_on_hover
        else:
            self.texture = self.texture_on_unhover

    def handle_mouse_click(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            self.function()
