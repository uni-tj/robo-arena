from pathlib import Path

import pygame
import pygame.locals

from roboarena.shared.block import Block, BlockCtx, FloorBlock, WallBlock
from roboarena.shared.types import Level, TileMap
from roboarena.shared.util import getBounds
from roboarena.shared.utils.vector import Vector


def tilesmap2levelmap(tm: TileMap) -> Level:
    (v_min, _) = getBounds(list(tm.keys()))
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
            bcoord = (v_min + tcoord + gcoord).round()
            level[bcoord] = generateBlock(bctx, bl)
    return level


def generateBlock(bc: BlockCtx, bs: dict[BlockCtx, Block]) -> Block:
    if bc in bs:
        return bs[bc]
    if bc.collision:
        return WallBlock(load_graphics(bc.graphics_path), Vector(65, 50))
    else:
        return FloorBlock(load_graphics(bc.graphics_path), Vector(65, 50))


def load_graphics(gp: Path) -> pygame.Surface:
    return pygame.image.load(gp)
