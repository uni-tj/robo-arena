import random
from collections.abc import Iterable
from functools import cache
from typing import Callable

import numpy as np
from numpy.typing import NDArray

from roboarena.shared.utils.perf_tester import PerformanceTester
from roboarena.shared.utils.vector import Vector


def gen_coord_space(
    xbounds: tuple[int, int], ybounds: tuple[int, int]
) -> Iterable[Vector[int]]:
    """Generates a list of coordinates in the rectangle given by xbounds and ybounds

    Args:
        xbounds (tuple[int, int]): (min x val, max x val)
        ybounds (tuple[int, int]): (min y val, may y val)

    Returns:
        list[Vector[int]]: list of Vector coordinates
            in the space defined by xbounds and ybounds
    """
    lnx = np.linspace(xbounds[0], xbounds[1] - 1, xbounds[1] - xbounds[0])
    lny = np.linspace(ybounds[0], ybounds[1] - 1, ybounds[1] - ybounds[0])
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    return [Vector.from_sequence(coord) for coord in coords]


@cache
def square_space(apothem: int) -> Iterable[Vector[int]]:
    return gen_coord_space((-apothem, apothem), (-apothem, apothem))


def square_space_around_wfc(center: Vector[int], apothem: int) -> list[Vector[int]]:
    return [(pos + center).round() for pos in square_space(apothem)]


type Tcoord = tuple[int, int]
type TupleVector = tuple[int, int]


def gen_coord_space_fast(
    xbounds: tuple[int, int], ybounds: tuple[int, int]
) -> Iterable[Tcoord]:
    """Generates a list of coordinates in the rectangle given by xbounds and ybounds

    Args:
        xbounds (tuple[int, int]): (min x val, max x val)
        ybounds (tuple[int, int]): (min y val, may y val)

    Returns:
        list[Vector[int]]: list of Vector coordinates
            in the space defined by xbounds and ybounds
    """
    lnx = np.linspace(xbounds[0], xbounds[1] - 1, xbounds[1] - xbounds[0])
    lny = np.linspace(ybounds[0], ybounds[1] - 1, ybounds[1] - ybounds[0])
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)
    return coords


@cache
def square_space_fast(apothem: int) -> Iterable[Tcoord]:
    return gen_coord_space_fast((-apothem, apothem), (-apothem, apothem))


def square_space_around_fast(center: tuple[int, int], apothem: int) -> list[Tcoord]:
    cx, cy = center
    return [(cx + x, cy + y) for (x, y) in square_space_fast(apothem)]


def vector_square_space_around_fast(
    center: Vector[int], apothem: int
) -> list[Vector[int]]:
    return [
        tcoord2vector(tc) for tc in square_space_around_fast(center.to_tuple(), apothem)
    ]


@cache
def gen_square_space_fast_2(apothem: int) -> Iterable[TupleVector]:
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


def square_space_around_fast_2(
    center: tuple[int, int], apothem: int
) -> Iterable[TupleVector]:
    cx, cy = center
    return ((cx + x, cy + y) for (x, y) in gen_square_space_fast_2(apothem))


def square_space_wfc_fast(center: Vector[int], apothem: int) -> list[Vector[int]]:
    return [
        tcoord2vector(tc)
        for tc in square_space_around_fast_2(center.to_tuple(), apothem)
    ]


def gen_square_space_wfc_fast_gen(
    center: Vector[int], apothem: int
) -> Iterable[Vector[int]]:
    return (
        tcoord2vector(tc)
        for tc in square_space_around_fast_2(center.to_tuple(), apothem)
    )


@cache
def tcoord2vector(tc: Tcoord) -> Vector[int]:
    return Vector.from_sequence(tc)


if __name__ == "__main__":
    # Tests for Addition of tuples, np.array and vector
    type TupleTupleVector = tuple[TupleVector, TupleVector]

    k = 100_000_000

    def gen_data() -> TupleTupleVector:
        return (
            (random.randint(-1000, 1000), random.randint(-1000, 1000)),
            (random.randint(-1000, 1000), random.randint(-1000, 1000)),
        )

    add_test = PerformanceTester(100_000, gen_data)

    cusom_vec_data: Callable[
        [tuple[tuple[int, int], tuple[int, int]]], tuple[Vector[int], Vector[int]]
    ] = lambda x: (Vector.from_sequence(x[0]), Vector.from_sequence(x[1]))

    def numpy_arr_data(
        tt: tuple[TupleVector, TupleVector]
    ) -> tuple[NDArray[np.uint64], NDArray[np.uint64]]:
        return np.array(tt[0]), np.array(tt[1])

    def default_add[T](x: tuple[T, T]) -> T:
        return x[0] + x[1]  # type:ignore

    tuple_data: Callable[[TupleTupleVector], TupleTupleVector] = lambda x: x

    def tuple_add(x: tuple[TupleVector, TupleVector]) -> TupleVector:
        return (x[0][0] + x[1][0], x[0][1] + x[1][1])

    type NpTupleVector = tuple[np.int64, np.int64]
    type NpTupleVectorTuple = tuple[NpTupleVector, NpTupleVector]

    def numpy_int_tuple_data(x: TupleTupleVector):
        return (
            (np.int64(x[0][0]), np.int64(x[0][1])),
            (np.int64(x[1][0]), np.int64(x[1][1])),
        )

    def ovtnp(x: NpTupleVectorTuple) -> NpTupleVector:
        return (x[0][0] + x[1][0], x[0][1] + x[1][1])

    add_test.add_function("vector", default_add, cusom_vec_data)
    add_test.add_function("nparray", default_add, numpy_arr_data)
    add_test.add_function("tuple int", tuple_add, tuple_data)
    add_test.add_function("tuple np_int", ovtnp, numpy_int_tuple_data)
    add_test.compare_performance()

    # Performance Test for vector space generation
    def gen_data_sq() -> tuple[TupleVector, int]:
        return (
            (random.randint(1, 100), random.randint(1, 100)),
            random.randint(1, 100),
        )

    sq_test = PerformanceTester(1000, gen_data_sq)
    type Sqi = tuple[Tcoord, int]

    def vssfd(x: Sqi) -> list[Vector[int]]:
        return vector_square_space_around_fast(Vector.from_sequence(x[0]), x[1])

    def vssd(x: Sqi) -> list[Vector[int]]:
        return square_space_around_wfc(Vector.from_sequence(x[0]), x[1])

    def vssf2d(x: Sqi) -> list[Vector[int]]:
        return square_space_wfc_fast(Vector.from_sequence(x[0]), x[1])

    def vssfgd(x: Sqi) -> Iterable[Vector[int]]:
        return gen_square_space_wfc_fast_gen(Vector.from_sequence(x[0]), x[1])

    def tid(x: Sqi) -> Sqi:
        return x

    sq_test.add_function("fast", vssfd, tid)
    sq_test.add_function("fast_comp", vssf2d, tid)
    sq_test.add_function("fast_gen", vssfgd, tid)
    sq_test.add_function("old", vssd, tid)

    sq_test.compare_performance()
