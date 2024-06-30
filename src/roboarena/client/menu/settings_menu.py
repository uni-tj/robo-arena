from typing import TYPE_CHECKING, Callable

import pygame
from pygame import Surface

from roboarena.client.keys import read_key
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.text import Text
from roboarena.shared.util import load_graphic
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client

BACK_BUTTON_UH_TEXTURE = load_graphic("buttons/button-back-unhover.png")
BACK_BUTTON_H_TEXTURE = load_graphic("buttons/button-back-hover.png")
SOUND_BUTTON_MUTE_TEXTURE = load_graphic("buttons/button-sound-mute.png")
SOUND_BUTTON_UNMUTE_TEXTURE = load_graphic("buttons/button-sound-unmute.png")
UP_BUTTON_UH_TEXTURE = load_graphic("buttons/button-upkey-unhover.png")
UP_BUTTON_H_TEXTURE = load_graphic("buttons/button-upkey-hover.png")
DOWN_BUTTON_UH_TEXTURE = load_graphic("buttons/button-downkey-unhover.png")
DOWN_BUTTON_H_TEXTURE = load_graphic("buttons/button-downkey-hover.png")
LEFT_BUTTON_UH_TEXTURE = load_graphic("buttons/button-leftkey-unhover.png")
LEFT_BUTTON_H_TEXTURE = load_graphic("buttons/button-leftkey-hover.png")
RIGHT_BUTTON_UH_TEXTURE = load_graphic("buttons/button-rightkey-unhover.png")
RIGHT_BUTTON_H_TEXTURE = load_graphic("buttons/button-rightkey-hover.png")


class SettingsMenu(Menu):

    def __init__(self, screen: Surface, main_menue: Menu, client: "Client"):

        close = super().close

        def switch_to_main_menue() -> None:
            close()
            main_menue.loop()

        def toggle_sound() -> None:

            unmute_texture = SOUND_BUTTON_UNMUTE_TEXTURE
            mute_texture = SOUND_BUTTON_MUTE_TEXTURE

            if pygame.mixer.get_busy():
                pygame.mixer.pause()
                buttons["mute_button"].texture_uh = mute_texture
                buttons["mute_button"].texture_h = unmute_texture
            else:
                pygame.mixer.unpause()
                buttons["mute_button"].texture_uh = unmute_texture
                buttons["mute_button"].texture_h = mute_texture

        def change_key(key: str) -> Callable[[], None]:
            return lambda: read_key(key)

        buttons: dict[str, Button] = {
            "mute_button": Button(
                SOUND_BUTTON_UNMUTE_TEXTURE,
                SOUND_BUTTON_MUTE_TEXTURE,
                Vector(50, 25),
                toggle_sound,
            ),
            "back_button": Button(
                BACK_BUTTON_UH_TEXTURE,
                BACK_BUTTON_H_TEXTURE,
                Vector(20, 70),
                switch_to_main_menue,
            ),
            "up_button": Button(
                UP_BUTTON_UH_TEXTURE,
                UP_BUTTON_H_TEXTURE,
                Vector(50, 45),
                change_key("key_up"),
            ),
            "down_button": Button(
                DOWN_BUTTON_UH_TEXTURE,
                DOWN_BUTTON_H_TEXTURE,
                Vector(50, 60),
                change_key("key_down"),
            ),
            "left_button": Button(
                LEFT_BUTTON_UH_TEXTURE,
                LEFT_BUTTON_H_TEXTURE,
                Vector(50, 75),
                change_key("key_left"),
            ),
            "right_button": Button(
                RIGHT_BUTTON_UH_TEXTURE,
                RIGHT_BUTTON_H_TEXTURE,
                Vector(50, 90),
                change_key("key_right"),
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text("  Settings  ", 100, Vector(50, 5)),
            "info_mute": Text("  Toggle sound  ", 100, Vector(50, 15)),
            "info_keys": Text(
                "Click button and hit key to change key binding", 100, Vector(50, 35)
            ),
        }

        super().__init__(
            screen, ((80, 80, 80), (140, 140, 140)), buttons, text_fields, client
        )
