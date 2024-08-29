from typing import TYPE_CHECKING, Callable, Tuple

from pygame import Surface, mixer

from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.renderable import Renderable
from roboarena.shared.rendering.util import size_from_texture_height
from roboarena.shared.util import sound_path
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import MenuRenderCtx

BUTTON_HOVER_SOUND_PATH = sound_path("menu/button-hover.mp3")
BUTTON_CLICK_SOUND_PATH = sound_path("menu/button-click.mp3")


class Button(Renderable):
    texture_uh: Surface
    texture_h: Surface
    texture_size: Vector[float]
    function: Callable[[], None]
    _mouse_over: bool = False
    _master_mixer: MasterMixer
    _hover_sound: mixer.Sound
    _click_sound: mixer.Sound

    def __init__(
        self,
        texture_uh: Surface,
        texture_h: Surface,
        position_pct: Vector[int],
        function: Callable[[], None],
        master_mixer: MasterMixer,
    ) -> None:
        texture_size = size_from_texture_height(texture_uh, height=1.3)
        super().__init__(position_pct, texture_uh, texture_size)
        self.texture_uh = texture_uh
        self.texture_h = texture_h
        self.function = function
        self._master_mixer = master_mixer
        self._hover_sound = master_mixer.load_sound(BUTTON_HOVER_SOUND_PATH)
        self._click_sound = master_mixer.load_sound(BUTTON_CLICK_SOUND_PATH)

    def mouse_over(self, mouse_pos_px: Tuple[int, int]) -> bool:
        return (
            self.position_px.x
            <= mouse_pos_px[0]
            <= self.position_px.x + self.dimensions_px.x
            and self.position_px.y
            <= mouse_pos_px[1]
            <= self.position_px.y + self.dimensions_px.y
        )

    def render(self, ctx: "MenuRenderCtx") -> None:
        super().render(ctx)

    def handle_mouse_pos(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            if (
                not self._master_mixer.is_sound_playing(self._hover_sound)
                and not self._mouse_over
            ):
                self._master_mixer.play_sound(self._hover_sound)
            self._mouse_over = True
            self.texture = self.texture_h
        else:
            self.texture = self.texture_uh
            self._mouse_over = False

    def handle_mouse_click(self, mouse_pos_px: Tuple[int, int]) -> None:
        if self.mouse_over(mouse_pos_px):
            if not self._master_mixer.is_sound_playing(self._click_sound):
                self._master_mixer.play_sound(self._click_sound)
            self.function()
