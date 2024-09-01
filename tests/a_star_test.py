from roboarena.shared.utils.search import Grid, astar
from roboarena.shared.utils.vector import Vector


def grid_from_string(grid_string: list[str]) -> Grid:
    result: Grid = {}
    for y, row in enumerate(grid_string):
        for x, char in enumerate(row):
            result[Vector(x, y)] = char == " "
    return result


# Tests
def test_single_cell_start_is_goal():
    grid = grid_from_string(
        [
            " ",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(0, 0)
    result = astar(start, goal, grid)
    assert result == [start]


def test_straight_line_path():
    grid = grid_from_string(
        [
            "     ",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(4, 0)
    result = astar(start, goal, grid)
    expected = [Vector(0, 0), Vector(1, 0), Vector(2, 0), Vector(3, 0), Vector(4, 0)]
    assert result == expected


def test_unreachable_goal():
    grid = grid_from_string(
        [
            " X ",
            " X ",
            "   ",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(2, 2)
    result = astar(start, goal, grid)
    excepted = [Vector(0, 0), Vector(0, 1), Vector(0, 2), Vector(1, 2), Vector(2, 2)]
    assert result == excepted


def test_simple_path():
    grid = grid_from_string(
        [
            "     ",
            "XXXX ",
            "     ",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(4, 2)
    result = astar(start, goal, grid)
    expected = [
        Vector(0, 0),
        Vector(1, 0),
        Vector(2, 0),
        Vector(3, 0),
        Vector(4, 0),
        Vector(4, 1),
        Vector(4, 2),
    ]
    assert result == expected


def test_multiple_paths():
    grid = grid_from_string(
        [
            "      ",
            "XXXXX ",
            "      ",
            "XXXXX ",
            "      ",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(5, 4)
    result = astar(start, goal, grid)
    expected = [
        Vector(0, 0),
        Vector(1, 0),
        Vector(2, 0),
        Vector(3, 0),
        Vector(4, 0),
        Vector(5, 0),
        Vector(5, 1),
        Vector(5, 2),
        Vector(5, 3),
        Vector(5, 4),
    ]
    assert result == expected


def test_no_valid_start():
    grid = grid_from_string(
        [
            "X",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(0, 0)
    result = astar(start, goal, grid)
    assert result == []


def test_no_valid_goal():
    grid = grid_from_string(
        [
            " ",
            "X",
        ]
    )
    start = Vector(0, 0)
    goal = Vector(0, 1)
    result = astar(start, goal, grid)
    assert result == []


def test_complex_grid():
    grid = grid_from_string(
        [
            "XXXXXXXXXX",
            "X        X",
            "X  X  X  X",
            "X  X  X  X",
            "X        X",
            "XXXXXXXXXX",
        ]
    )
    start = Vector(1, 1)
    goal = Vector(8, 4)
    result = astar(start, goal, grid)
    expected = [
        Vector(1, 1),
        Vector(2, 1),
        Vector(3, 1),
        Vector(4, 1),
        Vector(5, 1),
        Vector(6, 1),
        Vector(7, 1),
        Vector(8, 1),
        Vector(8, 2),
        Vector(8, 3),
        Vector(8, 4),
    ]
    assert result == expected


def test_edge_case_corner():
    grid = grid_from_string(
        [
            "XXXXX",
            "X   X",
            "X X X",
            "X   X",
            "XXXXX",
        ]
    )
    start = Vector(1, 1)
    goal = Vector(3, 1)
    result = astar(start, goal, grid)
    expected = [Vector(1, 1), Vector(2, 1), Vector(3, 1)]
    assert result == expected


def test_snake_like_grid():
    grid = grid_from_string(
        [
            "XXXXXXXXXX",
            "X        X",
            "X XXXXXX X",
            "X        X",
            "X XXXXXX X",
            "X        X",
            "XXXXXXXXXX",
        ]
    )
    start = Vector(1, 1)
    goal = Vector(8, 5)
    result = astar(start, goal, grid)
    expected = [
        Vector(1, 1),
        Vector(2, 1),
        Vector(3, 1),
        Vector(4, 1),
        Vector(5, 1),
        Vector(6, 1),
        Vector(7, 1),
        Vector(8, 1),
        Vector(8, 2),
        Vector(8, 3),
        Vector(8, 4),
        Vector(8, 5),
    ]
    assert result == expected
