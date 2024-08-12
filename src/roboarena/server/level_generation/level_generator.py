import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeGuard

import roboarena.server.level_generation.wfc as wfc
from roboarena.shared.util import enumerate2d_vec, neighbours_horiz, neighbours_vert
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.block import Block

logger = logging.getLogger(f"{__name__}")

type BlockPosition = Vector[int]
type Level = dict[BlockPosition, "Block"]
type LevelUpdate = Iterable[tuple[BlockPosition, "Block"]]


@dataclass(frozen=True)
class Tile:
    blocks: Sequence[Sequence["Block"]]


def is_tile(x: Any) -> TypeGuard[Tile]:
    return isinstance(x, Tile)


def both_tile(x: tuple[Any, Any]) -> TypeGuard[tuple[Tile, Tile]]:
    return all(map(is_tile, x))


@dataclass(frozen=True)
class Tileset:
    blocks_per_tile: int
    """The edge length of a tile in blocks"""
    tiles: list[Tile]
    """Tiles. First element must be the fallback tile"""
    rules_horiz: Iterable[tuple[Tile, Tile]]
    """Possible horizontal patterns as (left, right)"""
    rules_vert: Iterable[tuple[Tile, Tile]]
    """Possible vertical patterns as (top, bottom)"""

    @staticmethod
    def from_example(
        example: str, tiles: dict[str, Tile | None], fallback: Tile
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
            [fallback] + list(filter(is_tile, tiles.values())),
            filter(both_tile, ((tiles[a], tiles[b]) for a, b in neighbours_horiz(mat))),
            filter(both_tile, ((tiles[a], tiles[b]) for a, b in neighbours_vert(mat))),
        )

    def to_wfc(self) -> wfc.Tileset:
        ts = self.tiles
        return wfc.Tileset(
            len(ts),
            frozenset((ts.index(a), ts.index(b)) for a, b in self.rules_horiz),
            frozenset((ts.index(a), ts.index(b)) for a, b in self.rules_vert),
        )


class LevelGenerator:
    """An adapter between the game core and the wfc algorithm"""

    _tileset: Tileset
    _wfc: wfc.WFC
    level: Level

    def __init__(self, tileset: Tileset) -> None:
        self._tileset = tileset
        self._wfc = wfc.WFC(tileset.to_wfc())
        self.level = {}

    def generate(self, positions: Iterable[BlockPosition]) -> LevelUpdate:
        collapsed = self._wfc.collapse(self._tile_pos(pos) for pos in positions)
        for tile_pos, tile_idx in collapsed:
            tile = self._tileset.tiles[tile_idx]
            for block_pos, block in enumerate2d_vec(tile.blocks):
                pos = tile_pos * self._tileset.blocks_per_tile + block_pos.mirror()
                self.level[pos] = block
                yield pos, block

    def _tile_pos(self, block_pos: BlockPosition) -> wfc.TilePosition:
        return block_pos // self._tileset.blocks_per_tile
