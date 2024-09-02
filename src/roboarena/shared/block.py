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
    render_above_entities: bool
    blocks_robot: bool
    blocks_bullet: bool

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture_width(self.texture, width=1.0)


@cache
def load_void_debug_texture() -> Surface:
    voidTexture = Surface((50, 50))
    voidTexture.fill((0, 0, 0))
    pygame.draw.circle(voidTexture, "blue", (25, 25), 10)
    return voidTexture


floor = Block(
    load_graphic("floor/floor1.PNG"),
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_room = Block(
    load_graphic("floor/floor2.PNG"),
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_room_spawn = Block(
    load_graphic("floor/floor-start.PNG"),
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_door = Block(
    load_graphic("doors/door-open.png"),
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
wall = Block(
    load_graphic("wall/wall.PNG"),
    render_above_entities=True,
    blocks_robot=True,
    blocks_bullet=True,
)
void = Block(
    load_graphic("void/void.PNG"),
    render_above_entities=True,
    blocks_robot=True,
    blocks_bullet=True,
)

room_blocks = set([floor_room, floor_room_spawn, floor_door])
