import os
from typing import TYPE_CHECKING, Callable

import pygame
from pygame import Surface

from roboarena.client.keys import read_key
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.text import Text
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client

BACK_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-back-unhover.PNG"
)
BACK_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-back-hover.PNG"
)

SOUND_BUTTON_MUTE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-sound-mute.PNG"
)

SOUND_BUTTON_UNMUTE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-sound-unmute.PNG"
)

UP_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-upkey-unhover.png"
)
UP_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-upkey-hover.PNG"
)

DOWN_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-downkey-unhover.PNG"
)
DOWN_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-downkey-hover.PNG"
)

LEFT_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-leftkey-unhover.PNG"
)
LEFT_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-leftkey-hover.PNG"
)

RIGHT_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__),"..", "..", "resources", "graphics", "buttons/button-rightkey-unhover.PNG"
)
RIGHT_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "graphics", "buttons/button-rightkey-hover.PNG"
)


class SettingsMenu(Menu):

    def __init__(self, screen: Surface, menus: list[Menu], client: "Client"):
        super().__init__(screen, ((80, 80, 80), (140, 140, 140)), {}, {}, menus, client)

        header = Text("Settings", 50, Vector(50, 5))
        super().add_text_field("header", header)

        back_button_uh_texture = pygame.transform.scale(
            pygame.image.load(BACK_BUTTON_UH_PATH), (100, 100)
        )
        back_button_h_texture = pygame.transform.scale(
            pygame.image.load(BACK_BUTTON_H_PATH), (100, 100)
        )

        deactivate = super().deactivate

        def switch_to_main_menue() -> None:
            deactivate()
            menus[0].menu_loop()

        back_button = Button(
            back_button_uh_texture,
            back_button_h_texture,
            Vector(20, 70),
            switch_to_main_menue,
        )

        super().add_button("back_button", back_button)

        info_mute = Text("Toggle sound", 30, Vector(50, 15))
        super().add_text_field("info_mute", info_mute)

        sound_button_mute_texture = pygame.transform.scale(
            pygame.image.load(SOUND_BUTTON_MUTE_PATH), (70, 70)
        )
        sound_button_unmute_texture = pygame.transform.scale(
            pygame.image.load(SOUND_BUTTON_UNMUTE_PATH), (70, 70)
        )

        add_button = super().add_button

        def toggle_sound() -> None:
            if pygame.mixer.get_busy():
                pygame.mixer.pause()
                add_button("mute_button", sound_button_muted)
            else:
                pygame.mixer.unpause()
                add_button("mute_button", sound_button_unmuted)

        sound_button_muted = Button(
            sound_button_mute_texture,
            sound_button_unmute_texture,
            Vector(50, 25),
            toggle_sound,
        )
        sound_button_unmuted = Button(
            sound_button_unmute_texture,
            sound_button_mute_texture,
            Vector(50, 25),
            toggle_sound,
        )

        super().add_button("mute_button", sound_button_unmuted)

        info_keys = Text(
            "Click button and hit key to change key binding", 30, Vector(50, 35)
        )
        super().add_text_field("info_keys", info_keys)

        def change_key(key: str) -> Callable[[], None]:
            return lambda: read_key(key)

        up_button_uh_texture = pygame.transform.scale(
            pygame.image.load(UP_BUTTON_UH_PATH), (70, 70)
        )
        up_button_h_texture = pygame.transform.scale(
            pygame.image.load(UP_BUTTON_H_PATH), (70, 70)
        )

        up_button = Button(
            up_button_uh_texture,
            up_button_h_texture,
            Vector(50, 45),
            change_key("key_up"),
        )

        super().add_button("up_button", up_button)

        down_button_uh_texture = pygame.transform.scale(
            pygame.image.load(DOWN_BUTTON_UH_PATH), (70, 70)
        )
        down_button_h_texture = pygame.transform.scale(
            pygame.image.load(DOWN_BUTTON_H_PATH), (70, 70)
        )

        down_button = Button(
            down_button_uh_texture,
            down_button_h_texture,
            Vector(50, 60),
            change_key("key_down"),
        )

        super().add_button("down_button", down_button)

        left_button_uh_texture = pygame.transform.scale(
            pygame.image.load(LEFT_BUTTON_UH_PATH), (70, 70)
        )
        left_button_h_texture = pygame.transform.scale(
            pygame.image.load(LEFT_BUTTON_H_PATH), (70, 70)
        )

        left_button = Button(
            left_button_uh_texture,
            left_button_h_texture,
            Vector(50, 75),
            change_key("key_left"),
        )

        super().add_button("left_button", left_button)

        right_button_uh_texture = pygame.transform.scale(
            pygame.image.load(RIGHT_BUTTON_UH_PATH), (70, 70)
        )
        right_button_h_texture = pygame.transform.scale(
            pygame.image.load(RIGHT_BUTTON_H_PATH), (70, 70)
        )

        right_button = Button(
            right_button_uh_texture,
            right_button_h_texture,
            Vector(50, 90),
            change_key("key_right"),
        )

        super().add_button("right_button", right_button)
