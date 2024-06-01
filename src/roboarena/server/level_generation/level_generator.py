# from roboarena.server.level_generation.level_processing import Level
from roboarena.server.level_generation.level_processing import tilesmap2levelmap
from roboarena.server.level_generation.wfc import (
    Direction,
    TileType,
    UserConstraint,
    UserConstraintList,
    WfcCtx,
    generate_constraint_map,
    wave_function_collapse,
)
from roboarena.shared.types import Level
from roboarena.shared.util import dict_diff_keys
from roboarena.shared.utils.vector import Vector


class LevelGenerator:
    wfc_ctx: WfcCtx
    ConstraintMap: UserConstraintList
    new_diff: bool
    last_level: Level
    tilesize: Vector[int]
    tileset: set[TileType]

    def __init__(self) -> None:
        self.wfc_ctx = WfcCtx({}, {})
        self.ucm = [
            UserConstraint(
                [Direction.RIGHT, Direction.LEFT],
                TileType.H,
                [
                    TileType.H,
                    TileType.C,
                    TileType.E,
                    TileType.EI,
                    TileType.T,
                    TileType.TI,
                ],
            ),
            UserConstraint(
                [Direction.UP, Direction.DOWN],
                TileType.V,
                [
                    TileType.V,
                    TileType.C,
                    TileType.E,
                    TileType.EI,
                    TileType.T,
                    TileType.TI,
                ],
            ),
            UserConstraint(
                [Direction.LEFT, Direction.RIGHT],
                TileType.C,
                [TileType.H, TileType.T, TileType.TI, TileType.C],
            ),
            UserConstraint(
                [Direction.UP, Direction.DOWN],
                TileType.C,
                [TileType.V, TileType.E, TileType.EI, TileType.C],
            ),
            UserConstraint(
                [Direction.UP],
                TileType.C,
                [TileType.T],
            ),
            UserConstraint(
                [Direction.DOWN],
                TileType.C,
                [TileType.TI],
            ),
            UserConstraint(
                [Direction.LEFT],
                TileType.C,
                [TileType.E],
            ),
            UserConstraint(
                [Direction.RIGHT],
                TileType.C,
                [TileType.EI],
            ),
            UserConstraint(
                [Direction.RIGHT, Direction.DOWN, Direction.UP],
                TileType.E,
                [TileType.V, TileType.C, TileType.T, TileType.TI],
            ),
            UserConstraint(
                [Direction.LEFT, Direction.DOWN, Direction.UP],
                TileType.EI,
                [TileType.V, TileType.C, TileType.T, TileType.TI],
            ),
            UserConstraint(
                [Direction.RIGHT, Direction.LEFT, Direction.DOWN],
                TileType.T,
                [
                    TileType.H,
                    TileType.C,
                    TileType.E,
                    TileType.EI,
                    TileType.V,
                    TileType.TI,
                ],
            ),
            UserConstraint(
                [Direction.RIGHT, Direction.LEFT, Direction.UP],
                TileType.TI,
                [
                    TileType.H,
                    TileType.C,
                    TileType.E,
                    TileType.EI,
                    TileType.V,
                    TileType.T,
                ],
            ),
        ]
        self.last_level: Level = {}
        self.new_diff: bool = True
        self.tilesize = Vector(5, 5)  # TODO needs to be changed
        self.tileset = set()
        self.cm = generate_constraint_map(self.ucm)

    def get_level(self) -> Level:
        tm = self.wfc_ctx.nodes
        new_level: Level = tilesmap2levelmap(tm)
        if self.new_diff:
            self.last_level = new_level
            self.new_diff = False
        return new_level

    def get_level_diff(self) -> Level:
        return dict_diff_keys(self.last_level, self.get_level())

    def extend_level(self, posm: list[Vector[float]]) -> Level:
        tpos: list[Vector[int]] = map(lambda x: x.round(), posm / self.tilesize)
        self.wfc_ctx.add_nodes(tpos, set(x for x in TileType.__members__.values()))
        wave_function_collapse(self.wfc_ctx, self.cm)
        self.new_diff = True
        return self.get_level_diff()
