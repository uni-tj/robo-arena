from typing import TYPE_CHECKING, Callable

from pygame import Surface

from roboarena.client.keys import read_key
from roboarena.client.master_mixer import MasterMixer
from roboarena.client.menu.button import Button
from roboarena.client.menu.menu import Menu
from roboarena.client.menu.text import Text
from roboarena.shared.constants import (
    ButtonPos,
    Colors,
    Graphics,
    TextContent,
    TextPos,
    TextSize,
)

if TYPE_CHECKING:
    from roboarena.client.client import Client


class SettingsMenu(Menu):

    def __init__(
        self,
        screen: Surface,
        main_menu: Menu,
        client: "Client",
        master_mixer: MasterMixer,
    ) -> None:
        def switch_to_main_menu() -> None:
            self.close()
            main_menu.loop()

        def toggle_sound() -> None:
            unmute_texture = Graphics.SOUND_BUTTON_UNMUTE
            mute_texture = Graphics.SOUND_BUTTON_MUTE
            mixer = master_mixer

            if not mixer.muted:
                mixer.mute()
                buttons["mute_button"].texture_uh = mute_texture
                buttons["mute_button"].texture_h = unmute_texture
            else:
                mixer.unmute()
                buttons["mute_button"].texture_uh = unmute_texture
                buttons["mute_button"].texture_h = mute_texture

        def change_key(key: str) -> Callable[[], None]:
            return lambda: read_key(key, master_mixer)

        buttons: dict[str, Button] = {
            "mute_button": Button(
                Graphics.SOUND_BUTTON_UNMUTE,
                Graphics.SOUND_BUTTON_MUTE,
                ButtonPos.MUTE_BUTTON,
                toggle_sound,
                master_mixer,
            ),
            "back_button": Button(
                Graphics.BACK_BUTTON_UH,
                Graphics.BACK_BUTTON_H,
                ButtonPos.BACK_BUTTON,
                switch_to_main_menu,
                master_mixer,
            ),
            "up_button": Button(
                Graphics.UP_BUTTON_UH,
                Graphics.UP_BUTTON_H,
                ButtonPos.UP_BUTTON,
                change_key("key_up"),
                master_mixer,
            ),
            "down_button": Button(
                Graphics.DOWN_BUTTON_UH,
                Graphics.DOWN_BUTTON_H,
                ButtonPos.DOWN_BUTTON,
                change_key("key_down"),
                master_mixer,
            ),
            "left_button": Button(
                Graphics.LEFT_BUTTON_UH,
                Graphics.LEFT_BUTTON_H,
                ButtonPos.LEFT_BUTTON,
                change_key("key_left"),
                master_mixer,
            ),
            "right_button": Button(
                Graphics.RIGHT_BUTTON_UH,
                Graphics.RIGHT_BUTTON_H,
                ButtonPos.RIGHT_BUTTON,
                change_key("key_right"),
                master_mixer,
            ),
        }

        text_fields: dict[str, Text] = {
            "header": Text(
                TextContent.HEADER_SETTINGS,
                TextSize.STANDARD_SIZE,
                TextPos.HEADER_SETTINGS,
            ),
            "info_mute": Text(
                TextContent.INFO_MUTE, TextSize.STANDARD_SIZE, TextPos.INFO_MUTE
            ),
            "info_keys": Text(
                TextContent.INFO_KEYS, TextSize.STANDARD_SIZE, TextPos.INFO_KEYS
            ),
        }

        super().__init__(
            screen,
            Colors.BACKGROUND_GRADIENT,
            buttons,
            text_fields,
            client,
            master_mixer,
        )
