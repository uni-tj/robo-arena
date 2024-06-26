from abc import ABC
from typing import TYPE_CHECKING, List, Tuple

import pygame
from pygame import Rect, Surface

from roboarena.client.menu.button import Button
from roboarena.client.menu.text import Text
from roboarena.shared.rendering.renderer import MenuRenderer, RenderCtx
from roboarena.shared.util import Stopped, gradientRect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client


class Menu(ABC):
    _client: "Client"
    screen: Surface
    background_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]]
    background_texture: Surface
    buttons: dict[str, Button]
    text_fields: dict[str, Text]
    active: bool = False
    ctx: RenderCtx
    menus: List["Menu"]
    renderer: MenuRenderer

    def __init__(
        self,
        screen: Surface,
        background_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]],
        buttons: dict[str, Button],
        text_fields: dict[str, Text],
        menus: List["Menu"],
        client: "Client",
    ) -> None:
        self.screen = screen
        self.background_colors = background_colors
        self.buttons = buttons
        self.text_fields = text_fields
        self.menus = menus
        self.ctx = RenderCtx(screen, Vector(0, 0), {})
        self.create_background_texture()
        self._client = client
        self.renderer = MenuRenderer(screen)

    def add_button(self, key: str, button: Button) -> None:
        self.buttons[key] = button

    def add_text_field(self, key: str, text_field: Text) -> None:
        self.text_fields[key] = text_field

    def create_background_texture(self) -> None:
        self.background_texture = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        gradientRect(
            self.background_texture,
            self.background_colors[0],
            self.background_colors[1],
            Rect(0, 0, self.screen.get_width(), self.screen.get_height()),
        )
        self.background_texture.convert()
    

    def handle_mouse_pos(self, mouse_pos_px: Tuple[int, int]) -> None:
        for button in self.buttons.values():
            button.handle_mouse_pos(mouse_pos_px)

    def handle_mouse_click(self, mouse_pos_px: Tuple[int, int]) -> None:
        for button in self.buttons.values():
            button.handle_mouse_click(mouse_pos_px)

    def menu_loop(self) -> Stopped | None:
        self.active = True
        while self.active:
            if self._client.stopped.get():
                return Stopped() 
            for ev in pygame.event.get():
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(pygame.mouse.get_pos())
            self.handle_mouse_pos(pygame.mouse.get_pos())
            self.create_background_texture()
            self.renderer.render(self)

    def deactivate(self) -> None:
        self.active = False
