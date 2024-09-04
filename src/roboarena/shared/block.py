import logging
from abc import ABC
from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from roboarena.shared.constants import Graphics, TextureSize
from roboarena.shared.rendering.util import size_from_texture_width
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


@dataclass(frozen=True)
class Block(ABC):
    """
    A small 1x1 game units square of the level

    Of each block type there exists only one instance,
    as there would be too many instances otherwise.
    """

    texture: Surface
    render_above_entities: bool
    blocks_robot: bool
    blocks_bullet: bool

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture_width(self.texture, width=TextureSize.BLOCK_WIDTH)


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
crate = Block(
    Graphics.CRATE,
    render_above_entities=True,
    blocks_robot=True,
    blocks_bullet=True,
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
"""Blocks that are part of a room structure"""
