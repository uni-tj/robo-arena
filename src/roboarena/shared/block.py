import logging
from abc import ABC
from dataclasses import dataclass
from functools import cache, cached_property

import pygame
from pygame import Surface

from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.util import load_graphic
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")
STANDARD_BLOCK_SIZE_PX = 50


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture_width(self.texture, width=1.0)


@cache
def load_void_texture() -> Surface:
    voidTexture = Surface((50, 50))
    voidTexture.fill((0, 0, 0))
    # pygame.draw.circle(voidTexture, "blue", (25, 25), 10)
    return voidTexture


floor = Block(load_graphic("floor/floor2.PNG"))
floor_room_spawn = Block(load_graphic("floor/floor2.PNG"))
floor_door = Block(load_graphic("floor/floor2.PNG"))
wall = Block(load_graphic("walls/wall-top.PNG"))
void = Block(load_void_texture())
