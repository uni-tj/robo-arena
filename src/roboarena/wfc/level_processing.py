import pygame.locals
from roboarena.rendering_interface import Block, BlockCtx, Level, FloorBlock, WallBlock
from roboarena.utils.vector import Vector, getBounds
from typing import Optional
from roboarena.wfc.wfc import TileType, Tile
from pathlib import Path
import pygame

type TileMap = dict[Vector[int], Optional[Tile]]


def tilesmap2levelmap(tm: TileMap, tilesize: Vector[int]) -> Level:
    (v_min, v_max) = getBounds(list(tm.keys()))
    # (min_x, min_y) = v_min.tuple_repr()
    # (max_x, max_y) = v_max.tuple_repr()
    level: Level = {}
    bl: dict[BlockCtx, Block] = {}
    for tcoord, tile in tm.items():
        if tile is None:
            raise ValueError(
                """Not all tiles were filled after the application
                of wave function collapse"""
            )
        for gcoord, bctx in tile.graphics.items():
            bcoord = v_min + tcoord + gcoord
            level[bcoord] = generateBlock(bctx, bl)
    return level


def generateBlock(bc: BlockCtx, bs: dict[BlockCtx, Block]) -> Block:
    if bc in bs:
        return bs[bc]
    if bc.collision:
        return WallBlock(load_graphics(bc.graphics_path))
    else:
        return FloorBlock(load_graphics(bc.graphics_path))


def load_graphics(gp: Path) -> pygame.Surface:
    return pygame.image.load(gp)
