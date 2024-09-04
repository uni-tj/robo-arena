import logging
from abc import ABC
from dataclasses import dataclass
from functools import cache, cached_property

import pygame
from pygame import Surface

from roboarena.shared.constants import Graphics, TextureSize
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface
    render_above_entities: bool
    blocks_robot: bool
    blocks_bullet: bool

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture_width(self.texture, width=TextureSize.BLOCK_WIDTH)


@cache
def load_void_debug_texture() -> Surface:
    void_texture = Surface((50, 50))
    void_texture.fill((0, 0, 0))
    pygame.draw.circle(void_texture, "blue", (25, 25), 10)
    return void_texture


floor = Block(
    Graphics.FLOOR_1,
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_room = Block(
    Graphics.FLOOR_2,
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_room_spawn = Block(
    Graphics.FLOOR_START,
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
floor_door = Block(
    Graphics.DOOR_OPEN,
    render_above_entities=False,
    blocks_robot=False,
    blocks_bullet=False,
)
wall = Block(
    Graphics.WALL,
    render_above_entities=True,
    blocks_robot=True,
    blocks_bullet=True,
)
void = Block(
    Graphics.VOID,
    render_above_entities=True,
    blocks_robot=True,
    blocks_bullet=True,
)

room_blocks = set([floor_room, floor_room_spawn, floor_door])
