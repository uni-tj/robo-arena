import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TypeGuard

from more_itertools import iterate, take

import roboarena.server.level_generation.wfc as wfc
from roboarena.shared.types import BlockPosition, Level, LevelUpdate
from roboarena.shared.block import crate, floor_room
from roboarena.shared.constants import PerlinNoiseConstants
from roboarena.shared.util import enumerate2d_vec, neighbours_horiz, neighbours_vert
from roboarena.shared.utils.perlin_nose import perlin_noise_spot
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.block import Block

logger = logging.getLogger(f"{__name__}")


@dataclass(frozen=True)
class Edge:
    """
    The type of one edge of a tile.

    If Tile A has edge I at the top and tile B has the same on the bottom,
    then tile B can be placed above tile A.

    Comparison by object identity:

    .. code-block:: python
        Edge() == Edge() # False
    """

    def __eq__(self, value: object) -> bool:
        return self is value

    def __hash__(self) -> int:
        return id(self)


@dataclass(frozen=True)
class Tile:
    blocks: Sequence[Sequence["Block"]]
    edges: tuple[Edge, Edge, Edge, Edge]
    """(top, right, bottom, left) specifies which tiles can neighbour each other"""


def is_tile(x: Any) -> TypeGuard[Tile]:
    return isinstance(x, Tile)


def both_tile(x: tuple[Any, Any]) -> TypeGuard[tuple[Tile, Tile]]:
    return all(map(is_tile, x))


def rotate(tile: Tile) -> Tile:
    """Rotate a tile right."""
    return Tile(
        tuple(zip(*reversed(tile.blocks))),
        (tile.edges[3], tile.edges[0], tile.edges[1], tile.edges[2]),
    )


def rotations(tile: Tile) -> Sequence[Tile]:
    return take(4, iterate(rotate, tile))


@dataclass(frozen=True)
class Tileset:
    blocks_per_tile: int
    """The edge length of a tile in blocks"""
    tiles: list[Tile]
    fallback: Tile
    """The tile placed when no other one is possible"""
    init: Tile
    """The tile placed at position 0,0"""
    rules_horiz: Iterable[tuple[Tile, Tile]]
    """Possible horizontal patterns as (left, right)"""
    rules_vert: Iterable[tuple[Tile, Tile]]
    """Possible vertical patterns as (top, bottom)"""

    @staticmethod
    def from_example(
        example: str, tiles: dict[str, Tile | None], fallback: Tile, init: Tile
    ) -> "Tileset":
        """Generate the tileset rules from an string example and a mapping.

        .. code-block:: python

            example = \"\"\"
            ┬┤
            ├┴
            \"\"\"

        """
        mat = example.split("\n")
        return Tileset(
            len(fallback.blocks),
            list(filter(is_tile, tiles.values())),
            fallback,
            init,
            filter(both_tile, ((tiles[a], tiles[b]) for a, b in neighbours_horiz(mat))),
            filter(both_tile, ((tiles[a], tiles[b]) for a, b in neighbours_vert(mat))),
        )

    @staticmethod
    def from_edges(tiles: Iterable[Tile], fallback: Tile, init: Tile):
        """
        Generate the tileset rules from the tile edges.

        If Tile A has edge I at the top and tile B has the same on the bottom,
        then tile B can be placed above tile A.
        """
        tiles = list(tiles)
        return Tileset(
            len(fallback.blocks),
            tiles,
            fallback,
            init,
            ((a, b) for a in tiles for b in tiles if a.edges[1] is b.edges[3]),
            ((a, b) for a in tiles for b in tiles if a.edges[2] is b.edges[0]),
        )

    def to_wfc(self) -> wfc.Tileset:
        index: Callable[[Tile], int] = lambda tile: self.tiles.index(tile) + 1
        return wfc.Tileset(
            len(self.tiles) + 1,
            frozenset((index(a), index(b)) for a, b in self.rules_horiz),
            frozenset((index(a), index(b)) for a, b in self.rules_vert),
        )


class LevelGenerator:
    """An adapter between the game core and the wfc algorithm"""

    _tileset: Tileset
    _wfc: wfc.WFC
    level: Level

    def __init__(self, tileset: Tileset) -> None:
        self._tileset = tileset
        collapsed = {Vector(0, 0): tileset.tiles.index(tileset.init) + 1}
        self._wfc = wfc.WFC.from_map(tileset.to_wfc(), collapsed)
        self.level = {}

    def generate(self, positions: Iterable[BlockPosition]) -> LevelUpdate:
        collapsed = self._wfc.collapse(self._tile_pos(pos) for pos in positions)
        level_update = list[tuple[BlockPosition, "Block"]]()
        for tile_pos, tile_idx in collapsed:
            tile = (
                self._tileset.fallback
                if tile_idx == 0
                else self._tileset.tiles[tile_idx - 1]
            )
            for block_pos, block in enumerate2d_vec(tile.blocks):
                pos = tile_pos * self._tileset.blocks_per_tile + block_pos.mirror()
                if (
                    block == floor_room
                    and perlin_noise_spot(
                        pos,
                        PerlinNoiseConstants.gridsize,
                        PerlinNoiseConstants.num_octaves,
                    )
                    > PerlinNoiseConstants.threshold
                ):
                    block = crate
                self.level[pos] = block
                level_update.append((pos, block))
        return level_update

    def _tile_pos(self, block_pos: BlockPosition) -> wfc.TilePosition:
        return block_pos // self._tileset.blocks_per_tile
