from abc import ABC
from typing import TYPE_CHECKING, Tuple

import pygame
from pygame import Rect, Surface

from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.button import Button
from roboarena.client.menu.text import Text
from roboarena.client.util import QuitEvent
from roboarena.shared.rendering.renderer import MenuRenderer, RenderCtx
from roboarena.shared.util import EventTarget, Stopped, gradientRect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client


class Menu(ABC):
    _client: "Client"
    _master_mixer: MasterMixer
    screen: Surface
    background_texture: Surface
    buttons: dict[str, Button]
    text_fields: dict[str, Text]
    closed: bool = False
    ctx: RenderCtx
    renderer: MenuRenderer
    events: EventTarget[QuitEvent]

    def __init__(
        self,
        screen: Surface,
        background_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]],
        buttons: dict[str, Button],
        text_fields: dict[str, Text],
        client: "Client",
        master_mixer: MasterMixer,
    ) -> None:
        self.screen = screen
        self.buttons = buttons
        self.text_fields = text_fields
        self._client = client
        self.ctx = RenderCtx(screen, Vector(0, 0), {})
        self.background_texture = self.create_background_texture(background_colors)
        self.renderer = MenuRenderer(screen)
        self._master_mixer = master_mixer
        self.events = EventTarget()

    def add_button(self, key: str, button: Button) -> None:
        self.buttons[key] = button

    def add_text_field(self, key: str, text_field: Text) -> None:
        self.text_fields[key] = text_field

    def create_background_texture(
        self, colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]]
    ) -> Surface:
        background_texture = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        gradientRect(
            background_texture,
            colors[0],
            colors[1],
            Rect(0, 0, self.screen.get_width(), self.screen.get_height()),
        )
        return background_texture.convert()

    def handle_mouse_pos(self, mouse_pos_px: Tuple[int, int]) -> None:
        for button in self.buttons.values():
            button.handle_mouse_pos(mouse_pos_px)

    def handle_mouse_click(self, mouse_pos_px: Tuple[int, int]) -> None:
        for button in self.buttons.values():
            button.handle_mouse_click(mouse_pos_px)

    def loop(self) -> Stopped | None:
        self.closed = False
        while not self.closed:
            if self._client.stopped.get():
                return Stopped()
            for ev in pygame.event.get():
                match ev.type:
                    case pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_click(pygame.mouse.get_pos())
                    case pygame.QUIT:
                        self.events.dispatch(QuitEvent())
                    case _:
                        continue
            self.handle_mouse_pos(pygame.mouse.get_pos())
            self.renderer.render(self)

    def close(self) -> None:
        self.closed = True
