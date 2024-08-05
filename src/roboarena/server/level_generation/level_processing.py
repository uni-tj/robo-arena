from roboarena.server.level_generation.tile import Tile
from roboarena.server.level_generation.wfc import Tiles
from roboarena.shared.block import floor, wall
from roboarena.shared.types import Level, TileType
from roboarena.shared.util import enumerate2d
from roboarena.shared.utils.vector import Vector


def tiles2level(tiles: Tiles, tilesize: Vector[int]) -> Level:
    level: Level = {}
    for tcoord, tile in tiles.items():
        if tile is None:
            msg = "Not all tiles were filled after the application of wave function collapse"  # noqa: B950
            raise ValueError(msg)
        blocks = TILES[tile].blocks
        for bcoord, block in enumerate2d(blocks):
            coord = (tcoord * tilesize + Vector.from_tuple(bcoord)).round()
            level[coord] = block
    return level


w = wall
f = floor

TILES = {
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
