from dataclasses import dataclass
from enum import Enum

from roboarena.shared.block import BlockCtx


@dataclass(frozen=True)
class Tile:
    type: "TileType"
    blocks: list[list[BlockCtx]]


@dataclass(frozen=True)
class BasicTile:
    tt: "TileType"


class TileType(Enum):
    C = "┼"
    TI = "┴"
    T = "┬"
    EI = "┤"
    E = "├"
    H = "─"
    V = "│"


# Unicode Symbols: Box Drawings Light
# https://www.compart.com/de/unicode/search?q=Box+Drawings+Light#characters
