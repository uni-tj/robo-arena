import os

import pygame
import yaml

SETTINGS_PATH: str = os.path.join(os.path.dirname(__file__), "settings.yml")


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


def read_key(key: str) -> None:
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    update_key(key, event.key)
                return
