from pathlib import Path

import pygame
import pygame.locals

from roboarena.server.level_generation.tile import Tile
from roboarena.shared.block import Block, BlockCtx, FloorBlock, WallBlock
from roboarena.shared.types import Level, TileMap, TileType
from roboarena.shared.util import getBounds
from roboarena.shared.utils.vector import Vector


def tilesmap2levelmap(tm: TileMap, tilesize: Vector[int]) -> Level:
    (v_min, _) = getBounds(list(tm.keys()))
    # (min_x, min_y) = v_min.to_tuple()
    # (max_x, max_y) = v_max.to_tuple()
    level: Level = {}
    bs: dict[BlockCtx, Block] = {}
    for tcoord, tile in tm.items():
        if tile is None:
            continue
            raise ValueError(
                """Not all tiles were filled after the application
                of wave function collapse"""
            )
        # for, bctx in tile.blocks.items():
        new_tiles = convert_Tile(tile).blocks
        for i, r in enumerate(new_tiles):
            for j, bctx in enumerate(r):
                gcoord = Vector(j, i)
                bcoord = (v_min + (tcoord * tilesize) + gcoord).round()
                level[bcoord] = generateBlock(bctx, bs)
    return level


def generateBlock(bc: BlockCtx, bs: dict[BlockCtx, Block]) -> Block:
    if bc in bs:
        return bs[bc]
    if bc.collision:

        block = WallBlock(
            pygame.transform.scale(pygame.image.load(bc.graphics_path), (50, 65)),
            Vector(50, 65),
        )
    else:
        block = FloorBlock(
            pygame.transform.scale(pygame.image.load(bc.graphics_path), (65, 50)),
            Vector(50, 50),
        )
    bs[bc] = block
    return block


def load_graphics(gp: Path) -> pygame.Surface:
    return pygame.image.load(gp)


PATH_PREFIX = "./src/roboarena/resources/graphics/"


w = BlockCtx(Path(PATH_PREFIX + "walls/wall-top.PNG"), True)
f = BlockCtx(Path(PATH_PREFIX + "/floor/floor2.PNG"), False)

TM = {
    TileType.C: Tile(
        TileType.C,
        blocks=[
            [w, f, f, f, w],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [w, f, f, f, w],
        ],
    ),
    TileType.TI: Tile(
        TileType.TI,
        blocks=[
            [w, f, f, f, w],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [w, w, w, w, w],
        ],
    ),
    TileType.T: Tile(
        TileType.T,
        blocks=[
            [w, w, w, w, w],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [w, f, f, f, w],
        ],
    ),
    TileType.E: Tile(
        TileType.E,
        blocks=[
            [w, f, f, f, w],
            [w, f, f, f, f],
            [w, f, f, f, f],
            [w, f, f, f, f],
            [w, f, f, f, w],
        ],
    ),
    TileType.EI: Tile(
        TileType.EI,
        blocks=[
            [w, f, f, f, w],
            [f, f, f, f, w],
            [f, f, f, f, w],
            [f, f, f, f, w],
            [w, f, f, f, w],
        ],
    ),
    TileType.V: Tile(
        TileType.V,
        blocks=[
            [w, f, f, f, w],
            [w, f, f, f, w],
            [w, f, f, f, w],
            [w, f, f, f, w],
            [w, f, f, f, w],
        ],
    ),
    TileType.H: Tile(
        TileType.H,
        blocks=[
            [w, w, w, w, w],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [f, f, f, f, f],
            [w, w, w, w, w],
        ],
    ),
}


def convert_Tile(bt: TileType) -> Tile:
    return TM[bt]
