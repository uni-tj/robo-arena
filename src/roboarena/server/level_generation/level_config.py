from roboarena.server.level_generation.tile import TileType
from roboarena.shared.types import Direction, UserConstraint, UserConstraintList

UCM: UserConstraintList = [
    UserConstraint(
        TileType.C,
        {
            Direction.UP: [TileType.E, TileType.EI, TileType.T],
            Direction.DOWN: [TileType.E, TileType.EI, TileType.TI],
            Direction.LEFT: [TileType.E, TileType.T, TileType.TI],
            Direction.RIGHT: [TileType.EI, TileType.T, TileType.TI],
        },
    ),
    UserConstraint(
        TileType.E,
        {
            # Direction.UP: [TileType.E, TileType.EI, TileType.T],
            # Direction.DOWN: [TileType.E, TileType.EI, TileType.TI],
            # Direction.RIGHT: [TileType.EI, TileType.TI, TileType.T],
            # Direction.LEFT: [TileType.EI],
            Direction.UP: [TileType.EI, TileType.T],
            Direction.DOWN: [TileType.EI, TileType.TI],
            Direction.RIGHT: [TileType.EI, TileType.TI, TileType.T],
            # Direction.LEFT: [TileType.EI],
        },
    ),
    UserConstraint(
        TileType.T,
        {
            Direction.UP: [TileType.TI],
            Direction.DOWN: [TileType.TI],
            Direction.LEFT: [TileType.TI],
            # Direction.LEFT: [TileType.TI, TileType.T],
            # Direction.RIGHT: [TileType.TI, TileType.T, TileType.EI],
            Direction.RIGHT: [TileType.TI, TileType.EI],
        },
    ),
    UserConstraint(
        TileType.V,
        {
            Direction.UP: [TileType.C, TileType.E, TileType.EI, TileType.T],
            Direction.DOWN: [
                TileType.C,
                TileType.E,
                TileType.EI,
                # TileType.V,
                TileType.TI,
            ],
            Direction.LEFT: [
                TileType.EI,
                TileType.V,
            ],
            Direction.RIGHT: [
                TileType.E,
                TileType.V,
            ],
        },
    ),
    UserConstraint(
        TileType.H,
        {
            Direction.LEFT: [
                TileType.C,
                TileType.E,
                TileType.T,
                TileType.TI,
            ],
            Direction.RIGHT: [
                TileType.C,
                TileType.EI,
                TileType.T,
                TileType.TI,
            ],
            Direction.UP: [
                TileType.TI,
                TileType.H,
            ],
            Direction.DOWN: [
                TileType.T,
                TileType.H,
            ],
        },
    ),
]
