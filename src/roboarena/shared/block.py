import logging
from abc import ABC
from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from roboarena.shared.constants import Graphics, TextureSize
from roboarena.shared.raytracing.tuple_util import Line
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
    blocks_light: bool
    blocks_robot: bool
    blocks_bullet: bool
    reflectivity: float = 0.0

    @staticmethod
    def edges_at(pos: Vector[int]):
        """The edges of the block"""
        res = (0, 1)
        return [
            Line.from_vects(pos, Vector(1, 0), res),  # type: ignore
            Line.from_vects(pos, Vector(0, 1), res),  # type: ignore
            Line.from_vects(pos + Vector.one(), Vector(-1, 0), res),  # type: ignore
            Line.from_vects(pos + Vector.one(), Vector(0, -1), res),  # type: ignore
        ]

    @staticmethod
    def get_normal(pos: Vector[int], point: Vector[float]):
        # Find the edge that the point is on.
        for edge in Block.edges_at(pos):
            if edge.is_on(point.to_tuple()):
                return edge.normal()

        # If the point is not on any edge, it's likely inside the block,
        # so return the normal vector of the closest edge.
        distances = [edge.distance(point.to_tuple()) for edge in Block.edges_at(pos)]
        closest_index = distances.index(min(distances))
        return Block.edges_at(pos)[closest_index].normal()

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture_width(self.texture, width=TextureSize.BLOCK_WIDTH)


floor = Block(
    Graphics.FLOOR_1,
    render_above_entities=False,
    blocks_robot=False,
    blocks_light=False,
    blocks_bullet=False,
    reflectivity=0.133,
)
floor_room = Block(
    Graphics.FLOOR_2,
    render_above_entities=False,
    blocks_light=False,
    blocks_robot=False,
    blocks_bullet=False,
    reflectivity=0.23,
)
floor_room_spawn = Block(
    Graphics.FLOOR_START,
    render_above_entities=False,
    blocks_light=False,
    blocks_robot=False,
    blocks_bullet=False,
    reflectivity=0,
)
floor_door = Block(
    Graphics.DOOR_OPEN,
    render_above_entities=False,
    blocks_light=False,
    blocks_robot=False,
    blocks_bullet=False,
    reflectivity=0,
)
crate = Block(
    Graphics.CRATE,
    render_above_entities=True,
    blocks_light=True,
    blocks_robot=True,
    blocks_bullet=True,
    reflectivity=0.4,
)
wall = Block(
    Graphics.WALL,
    render_above_entities=True,
    blocks_light=True,
    blocks_robot=True,
    blocks_bullet=True,
    reflectivity=0.5,
)
void = Block(
    Graphics.VOID,
    render_above_entities=False,
    blocks_light=False,
    blocks_robot=True,
    blocks_bullet=True,
    reflectivity=0.0,
)

room_blocks = set([floor_room, floor_room_spawn, floor_door])
"""Blocks that are part of a room structure"""
