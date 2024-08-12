import os

import pygame
import yaml

from roboarena.client.master_mixer import MasterMixer
from roboarena.shared.util import sound_path

SETTINGS_PATH: str = os.path.join(os.path.dirname(__file__), "settings.yml")
KEY_SET_SOUND_PATH: str = sound_path("menu/button-key-set.mp3")


def load_keys() -> dict[str, int]:
    with open(SETTINGS_PATH, "r") as file:
        settings = yaml.safe_load(file)
        return settings["keys"]


def save_keys(keys: dict[str, int]) -> None:
    with open(SETTINGS_PATH, "w") as file:
        yaml.dump({"keys": keys}, file)


def update_key(key: str, value: int) -> None:
    keys = load_keys()
    keys[key] = value
    save_keys(keys)


def read_key(key: str, master_mixer: MasterMixer) -> None:
    key_set_sound = master_mixer.load_sound(KEY_SET_SOUND_PATH)
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    update_key(key, event.key)
                    master_mixer.play_sound(key_set_sound)
                return
