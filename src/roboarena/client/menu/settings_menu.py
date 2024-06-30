import os
from typing import Callable

import pygame
from pygame import Surface

from roboarena.client.keys import read_key
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.text import Text
from roboarena.shared.util import load_texture
from roboarena.shared.utils.vector import Vector

BACK_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-back-unhover.png"
)
BACK_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-back-hover.png"
)

SOUND_BUTTON_MUTE_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-sound-mute.png"
)

SOUND_BUTTON_UNMUTE_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-sound-unmute.png"
)

UP_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-upkey-unhover.png"
)
UP_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-upkey-hover.png"
)

DOWN_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-downkey-unhover.png"
)
DOWN_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-downkey-hover.png"
)

LEFT_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-leftkey-unhover.png"
)
LEFT_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-leftkey-hover.png"
)

RIGHT_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-rightkey-unhover.png"
)
RIGHT_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-rightkey-hover.png"
)


class SettingsMenu(Menu):

    def __init__(self, screen: Surface, main_menue: Menu):

        deactivate = super().deactivate

        def switch_to_main_menue() -> None:
            deactivate()
            main_menue.menu_loop()

        def toggle_sound() -> None:

            unmute_texture = load_texture(SOUND_BUTTON_UNMUTE_PATH, (70, 70))
            mute_texture = load_texture(SOUND_BUTTON_MUTE_PATH, (70, 70))

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
                load_texture(SOUND_BUTTON_UNMUTE_PATH, (70, 70)),
                load_texture(SOUND_BUTTON_MUTE_PATH, (70, 70)),
                Vector(50, 25),
                toggle_sound,
            ),
            "back_button": Button(
                load_texture(BACK_BUTTON_UH_PATH, (100, 100)),
                load_texture(BACK_BUTTON_H_PATH, (100, 100)),
                Vector(20, 70),
                switch_to_main_menue,
            ),
            "up_button": Button(
                load_texture(UP_BUTTON_UH_PATH, (70, 70)),
                load_texture(UP_BUTTON_H_PATH, (70, 70)),
                Vector(50, 45),
                change_key("key_up"),
            ),
            "down_button": Button(
                load_texture(DOWN_BUTTON_UH_PATH, (70, 70)),
                load_texture(DOWN_BUTTON_H_PATH, (70, 70)),
                Vector(50, 60),
                change_key("key_down"),
            ),
            "left_button": Button(
                load_texture(LEFT_BUTTON_UH_PATH, (70, 70)),
                load_texture(LEFT_BUTTON_H_PATH, (70, 70)),
                Vector(50, 75),
                change_key("key_left"),
            ),
            "right_button": Button(
                load_texture(RIGHT_BUTTON_UH_PATH, (70, 70)),
                load_texture(RIGHT_BUTTON_H_PATH, (70, 70)),
                Vector(50, 90),
                change_key("key_right"),
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text("Settings", 50, Vector(50, 5)),
            "info_mute": Text("Toggle sound", 30, Vector(50, 15)),
            "info_keys": Text(
                "Click button and hit key to change key binding", 30, Vector(50, 35)
            ),
        }

        super().__init__(screen, ((80, 80, 80), (140, 140, 140)), buttons, text_fields)
