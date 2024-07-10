from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roboarena.shared.block import Block


@dataclass(frozen=True)
class Tile:
    type: "TileType"
    blocks: list[list["Block"]]


@dataclass(frozen=True)
class BasicTile:
    tt: "TileType"


class TileType(Enum):
    # A = "A"
    # B = "B"
    IM = " "
    C = "┼"
    TI = "┴"
    T = "┬"
    EI = "┤"
    E = "├"
    H = "─"
    V = "│"


# Unicode Symbols: Box Drawings Light
# https://www.compart.com/de/unicode/search?q=Box+Drawings+Light#characters
