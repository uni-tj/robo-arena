from functools import cache
from typing import Iterable

import numpy as np

from roboarena.shared.types import TupleVector
from roboarena.shared.utils.vector import Vector


@cache
def gen_square_space_fast(apothem: int) -> Iterable[TupleVector]:
    """Generates a list of coordinates in the square around 0,0 with given apothem
    Args:
        apthem: int (half the length of a square edge)

    Returns:
        list[Tcoord]: list of Tuple coordinates
            in the square defined by apothem
    """
    ln = np.linspace(-apothem, apothem, apothem * 2 + 1)
    coords = np.array(np.meshgrid(ln, ln)).ravel("F").reshape(-1, 2).astype(int)
    return coords


def gen_square_space_around_fast(
    center: tuple[int, int], apothem: int
) -> Iterable[TupleVector]:
    cx, cy = center
    return ((cx + x, cy + y) for (x, y) in gen_square_space_fast(apothem))


def gen_square_space_wfc_fast(
    center: Vector[int], apothem: int
) -> Iterable[Vector[int]]:
    return (
        tuple2vector(tc)
        for tc in gen_square_space_around_fast(center.to_tuple(), apothem)
    )


@cache
def tuple2vector(tc: TupleVector) -> Vector[int]:
    return Vector.from_sequence(tc)
