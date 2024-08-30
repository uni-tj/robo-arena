from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
from roboarena.shared.types import QuitEvent
from roboarena.shared.util import load_graphic, sound_path
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import Client

START_BUTTON_UH_TEXTURE = load_graphic("buttons/button-play-unhover.png")
START_BUTTON_H_TEXTURE = load_graphic("buttons/button-play-hover.png")
SETTINGS_BUTTON_UH_TEXTURE = load_graphic("buttons/button-settings-unhover.png")
SETTINGS_BUTTON_H_TEXTURE = load_graphic("buttons/button-settings-hover.png")

MENU_MUSIC_PATH = sound_path("menu/menu-music.mp3")


class MainMenu(Menu):

    def __init__(
        self, screen: Surface, client: "Client", master_mixer: MasterMixer
    ) -> None:
        settings_menu = SettingsMenu(screen, self, client, master_mixer)

        def switch_to_settings() -> None:
            self.close()
            settings_menu.loop()

        def play_game() -> None:
            self._master_mixer.stop_music()
            self.close()

        buttons: dict[str, Button] = {
            "start_button": Button(
                START_BUTTON_UH_TEXTURE,
                START_BUTTON_H_TEXTURE,
                Vector(50, 50),
                play_game,
                master_mixer,
            ),
            "settings_button": Button(
                SETTINGS_BUTTON_UH_TEXTURE,
                SETTINGS_BUTTON_H_TEXTURE,
                Vector(70, 70),
                switch_to_settings,
                master_mixer,
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text("RoboArena", 100, Vector(50, 10))
        }

        super().__init__(
            screen,
            ((80, 80, 80), (140, 140, 140)),
            buttons,
            text_fields,
            client,
            master_mixer,
        )
        settings_menu.events.add_listener(QuitEvent, self.events.dispatch)

    def loop(self) -> None:
        if not self._master_mixer.is_music_playing():
            self._master_mixer.play_music_loop(MENU_MUSIC_PATH)
        super().loop()
