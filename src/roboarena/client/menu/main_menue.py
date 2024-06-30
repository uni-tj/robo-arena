import os

from pygame import Surface

from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
from roboarena.shared.util import load_texture
from roboarena.shared.utils.vector import Vector

START_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-play-unhover.png"
)
START_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-play-hover.png"
)
SETTINGS_BUTTON_UH_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-settings-unhover.png"
)
SETTINGS_BUTTON_H_PATH = os.path.join(
    os.path.dirname(__file__), "resources/graphics/Buttons/button-settings-hover.png"
)


class MainMenu(Menu):

    def __init__(self, screen: Surface):

        deactivate = super().deactivate

        settings_menu = SettingsMenu(screen, self)

        def switch_to_settings() -> None:
            deactivate()
            settings_menu.menu_loop()

        buttons: dict[str, Button] = {
            "start_button": Button(
                load_texture(START_BUTTON_UH_PATH, (160, 100)),
                load_texture(START_BUTTON_H_PATH, (160, 100)),
                Vector(50, 50),
                deactivate,
            ),
            "settings_button": Button(
                load_texture(SETTINGS_BUTTON_UH_PATH, (100, 100)),
                load_texture(SETTINGS_BUTTON_H_PATH, (100, 100)),
                Vector(70, 70),
                switch_to_settings,
            ),
        }

        text_fields: dict[str, Text] = {"header": Text("RoboArena", 50, Vector(50, 10))}

        super().__init__(screen, ((80, 80, 80), (140, 140, 140)), buttons, text_fields)
