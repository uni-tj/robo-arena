from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
from roboarena.shared.util import load_graphic
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client

START_BUTTON_UH_TEXTURE = load_graphic("buttons/button-play-unhover.png")
START_BUTTON_H_TEXTURE = load_graphic("buttons/button-play-hover.png")
SETTINGS_BUTTON_UH_TEXTURE = load_graphic("buttons/button-settings-unhover.png")
SETTINGS_BUTTON_H_TEXTURE = load_graphic("buttons/button-settings-hover.png")


class MainMenu(Menu):

    def __init__(self, screen: Surface, client: "Client"):

        close = super().close

        settings_menu = SettingsMenu(screen, self, client)

        def switch_to_settings() -> None:
            close()
            settings_menu.loop()

        buttons: dict[str, Button] = {
            "start_button": Button(
                START_BUTTON_UH_TEXTURE,
                START_BUTTON_H_TEXTURE,
                Vector(50, 50),
                close,
            ),
            "settings_button": Button(
                SETTINGS_BUTTON_UH_TEXTURE,
                SETTINGS_BUTTON_H_TEXTURE,
                Vector(70, 70),
                switch_to_settings,
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text("RoboArena", 100, Vector(50, 10))
        }

        super().__init__(
            screen, ((80, 80, 80), (140, 140, 140)), buttons, text_fields, client
        )
