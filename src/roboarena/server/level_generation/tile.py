from dataclasses import dataclass
from enum import Enum

from roboarena.shared.block import BlockCtx
from roboarena.shared.utils.vector import Vector


@dataclass(frozen=True)
class Tile:
    color: str
    type: "TileType"
    graphics: dict[Vector[int], "BlockCtx"]

    def __str__(self) -> str:
        return self.color


class TileType(Enum):
    # R = "R"
    # B = "B"
    # C = "C"
    H = "─"
    V = "|"
    C = "┼"
    E = "├"
    EI = "┤"
    TI = "┴"
    T = "┬"
    # # N = "N"
    # UL = "UL"
    # UR = "UR"
    # BL = "BL"
    # BR = "BR"
