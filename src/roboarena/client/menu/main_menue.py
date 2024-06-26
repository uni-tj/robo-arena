import os

import pygame
from pygame import Surface

from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
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
        super().__init__(screen, ((80, 80, 80), (140, 140, 140)), {}, {}, [])
        settings_menu = SettingsMenu(screen, [self])

        header = Text("RoboArena", 50, Vector(50, 10))
        super().add_text_field("header", header)

        start_button_uh_texture = pygame.transform.scale(
            pygame.image.load(START_BUTTON_UH_PATH), (160, 100)
        )
        start_button_hover_texture = pygame.transform.scale(
            pygame.image.load(START_BUTTON_H_PATH), (160, 100)
        )

        deactivate = super().deactivate

        start_button = Button(
            start_button_uh_texture,
            start_button_hover_texture,
            Vector(50, 50),
            deactivate,
        )

        super().add_button("start_button", start_button)

        settings_button_texture = pygame.transform.scale(
            pygame.image.load(SETTINGS_BUTTON_UH_PATH), (100, 100)
        )
        settings_button_hover_texture = pygame.transform.scale(
            pygame.image.load(SETTINGS_BUTTON_H_PATH), (100, 100)
        )

        def switch_to_settings() -> None:
            deactivate()
            settings_menu.menu_loop()

        settings_button = Button(
            settings_button_texture,
            settings_button_hover_texture,
            Vector(70, 70),
            switch_to_settings,
        )

        super().add_button("settings_button", settings_button)
