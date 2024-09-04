import pygame
import yaml

from roboarena.client.master_mixer import MasterMixer
from roboarena.shared.constants import SettingPathConstants, SoundPath, SoundVolume


def load_keys() -> dict[str, int]:
    with open(SettingPathConstants.SETTINGS_PATH, "r") as file:
        settings = yaml.safe_load(file)
        return settings["keys"]


def save_keys(keys: dict[str, int]) -> None:
    with open(SettingPathConstants.SETTINGS_PATH, "w") as file:
        yaml.dump({"keys": keys}, file)


def update_key(key: str, value: int) -> None:
    keys = load_keys()
    keys[key] = value
    save_keys(keys)


def read_key(key: str, master_mixer: MasterMixer) -> None:
    key_set_sound = master_mixer.load_sound(SoundPath.KEY_SET_SOUND)
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    update_key(key, event.key)
                    master_mixer.set_sound_volume(key_set_sound, SoundVolume.KEY_SET)
                    master_mixer.play_sound(key_set_sound)
                return
