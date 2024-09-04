from typing import TYPE_CHECKING

from pygame import Surface

from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.settings_menu import SettingsMenu
from roboarena.client.menu.text import Text
from roboarena.shared.constants import (
    Colors,
    MusicPaths,
    MusicVolume,
    TextContent,
    TextPos,
    TextSize,
)
from roboarena.shared.types import QuitEvent

if TYPE_CHECKING:
    from roboarena.client.client import Client


class Endscreen(Menu):

    def __init__(
        self,
        screen: Surface,
        client: "Client",
        master_mixer: MasterMixer,
        score: int,
    ) -> None:
        settings_menu = SettingsMenu(screen, self, client, master_mixer)

        text_fields: dict[str, Text] = {
            "header": Text(
                TextContent.HEADER_ENDSCREEN,
                TextSize.STANDARD_SIZE,
                TextPos.HEADER_ENDSCREEN,
            ),
            "score": Text(
                f"Your Score: {score}",
                TextSize.STANDARD_SIZE,
                TextPos.SCORE,
            ),
        }

        super().__init__(
            screen,
            Colors.BACKGROUND_GRADIENT,
            dict(),
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
