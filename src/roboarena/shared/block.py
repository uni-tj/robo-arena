import logging
from abc import ABC
from dataclasses import dataclass
from functools import cache

import pygame
from pygame import Surface
from pygame.transform import scale_by

from roboarena.shared.util import load_graphic

logger = logging.getLogger(f"{__name__}")


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface


@cache
def load_void_texture() -> Surface:
    voidTexture = Surface((50, 50))
    voidTexture.fill((0, 0, 0))
    pygame.draw.circle(voidTexture, "blue", (25, 25), 10)
    return voidTexture


floor = Block(scale_by(load_graphic("floor/floor2.PNG"), 0.1))
floor_room_spawn = Block(scale_by(load_graphic("floor/floor2.PNG"), 0.1))
floor_door = Block(scale_by(load_graphic("floor/floor2.PNG"), 0.1))
wall = Block(scale_by(load_graphic("walls/wall-top.PNG"), 0.1))
void = Block(load_void_texture())
