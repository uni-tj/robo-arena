from roboarena.server.level_generation.tile import TileType
from roboarena.shared.types import Direction, UserConstraint, UserConstraintList

# UCM: UserConstraintList = [
#     UserConstraint(
#         TileType.A,
#         {
#             Direction.UP: [TileType.B],
#             Direction.DOWN: [TileType.B],
#             Direction.LEFT: [TileType.B],
#             Direction.RIGHT: [TileType.B],
#         },
#     )
# ]
TL = list(x for x in TileType.__members__.values())
UCM: UserConstraintList = [
    UserConstraint(
        TileType.IM,
        {
            Direction.UP: TL,
            Direction.DOWN: TL,
            Direction.LEFT: TL,
            Direction.RIGHT: TL,
        },
    ),
    UserConstraint(
        TileType.C,
        {
            Direction.UP: [TileType.E, TileType.EI, TileType.T, TileType.C],
            Direction.DOWN: [TileType.E, TileType.EI, TileType.TI, TileType.C],
            Direction.LEFT: [TileType.E, TileType.T, TileType.TI, TileType.C],
            Direction.RIGHT: [TileType.EI, TileType.T, TileType.TI, TileType.C],
        },
    ),
    UserConstraint(
        TileType.E,
        {
            # Direction.UP: [TileType.E, TileType.EI, TileType.T],
            # Direction.DOWN: [TileType.E, TileType.EI, TileType.TI],
            # Direction.RIGHT: [TileType.EI, TileType.TI, TileType.T],
            # Direction.LEFT: [TileType.EI],
            Direction.UP: [TileType.T],
            Direction.DOWN: [TileType.TI],
            # Direction.UP: [TileType.EI, TileType.E, TileType.T],
            # Direction.DOWN: [TileType.EI, TileType.E, TileType.TI],
            Direction.RIGHT: [TileType.EI, TileType.TI, TileType.T],
            Direction.LEFT: [TileType.EI],
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
            ],
            Direction.RIGHT: [
                TileType.E,
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
            ],
            Direction.DOWN: [
                TileType.T,
            ],
        },
    ),
]
