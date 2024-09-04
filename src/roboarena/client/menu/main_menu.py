from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
from roboarena.shared.constants import (
    ButtonPos,
    Colors,
    Graphics,
    MusicPaths,
    MusicVolume,
    TextContent,
    TextPos,
    TextSize,
)
from roboarena.shared.types import QuitEvent

if TYPE_CHECKING:
    from roboarena.client.client import Client


class MainMenu(Menu):

    def __init__(
        self,
        screen: Surface,
        client: "Client",
        master_mixer: MasterMixer,
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
                Graphics.START_BUTTON_UH,
                Graphics.START_BUTTON_H,
                ButtonPos.START_BUTTON,
                play_game,
                master_mixer,
            ),
            "settings_button": Button(
                Graphics.SETTINGS_BUTTON_UH,
                Graphics.SETTINGS_BUTTON_H,
                ButtonPos.SETTINGS_BUTTON,
                switch_to_settings,
                master_mixer,
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text(
                TextContent.HEADER_MAIN_MENU, TextSize.HEADER, TextPos.HEADER_MAIN_MENU
            )
        }

        super().__init__(
            screen,
            Colors.BACKGROUND_GRADIENT,
            buttons,
            text_fields,
            client,
            master_mixer,
        )
        settings_menu.events.add_listener(QuitEvent, self.events.dispatch)

    def loop(self) -> None:
        if not self._master_mixer.is_music_playing():
            self._master_mixer.set_music_volume(MusicVolume.MAIN_MENU)
            self._master_mixer.play_music_loop(MusicPaths.MENU_MUSIC)
        super().loop()
