from collections.abc import Iterable
from typing import Optional

from roboarena.shared.util import search_connected

type IntTuple2 = tuple[int, int]


def rectangle_to_dict(rectangle: list[str]) -> dict[IntTuple2, str]:
    result: dict[IntTuple2, str] = {}
    for row_index, row in enumerate(rectangle):
        for col_index, char in enumerate(row):
            result[(col_index, row_index)] = char
    return result


def neighbours(pos: IntTuple2) -> Iterable[IntTuple2]:
    for x in range(-1, 2):
        for y in range(-1, 2):
            if abs(x) + abs(y) != 1:
                continue

            yield pos[0] + x, pos[1] + y


def only_X(val: str) -> Optional[int]:
    return 1 if val == "X" else None


def test_single_included():
    data = rectangle_to_dict(
        [
            "X",
        ]
    )
    expected = set([(0, 0)])
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_single_excluded():
    data = rectangle_to_dict(
        [
            "A",
        ]
    )
    expected = set[IntTuple2]()
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_start_included_positions():
    data = rectangle_to_dict(
        [
            "      ",
            " XXXX ",
            "   XX ",
            "      ",
        ]
    )
    expected = set([(2, 1), (3, 1), (1, 1), (4, 2), (3, 2), (4, 1)])
    for pos in expected:
        results = search_connected(pos, data, only_X, neighbours)
        assert set(results.keys()) == expected


def test_start_excluded_position():
    data = rectangle_to_dict(
        [
            "      ",
            " XXXX ",
            "   XX ",
            "      ",
        ]
    )
    expected: set[IntTuple2] = set([])
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_no_diagonal_connection():
    data = rectangle_to_dict(
        [
            "X ",
            " X",
        ]
    )
    expected = set([(0, 0)])
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_multiple_disconnected_components():
    data = rectangle_to_dict(
        [
            "XAX",
            "   ",
            "XAX",
        ]
    )
    expected = set([(0, 0)])
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_snake_pattern():
    data = rectangle_to_dict(
        [
            "X    ",
            "XXXX ",
            "   X ",
            " XXX ",
            " X   ",
        ]
    )
    expected = set(
        [
            (0, 0),
            (0, 1),
            (1, 1),
            (2, 1),
            (3, 1),
            (3, 2),
            (1, 3),
            (2, 3),
            (3, 3),
            (1, 4),
        ]
    )
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_empty_grid():
    data: dict[IntTuple2, str] = {}
    expected = set[IntTuple2]()
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected


def test_edge_connection():
    data = rectangle_to_dict(
        [
            "X X X",
            "     ",
            "X   X",
        ]
    )
    expected = set([(0, 0)])
    results = search_connected((0, 0), data, only_X, neighbours)
    assert set(results.keys()) == expected
