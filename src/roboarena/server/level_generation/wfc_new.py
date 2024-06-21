import logging
import random
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np
from funcy import log_durations
from numpy.typing import NDArray

from roboarena.server.level_generation.level_config import UCM
from roboarena.server.level_generation.tile import BasicTile, TileType
from roboarena.server.level_generation.wfc import bcolors
from roboarena.shared.types import Direction, UserConstraint, UserConstraintList

# from roboarena.server.level_generation.tile import TileType
# from roboarena.server.level_generation.wfc import BasicTile
from roboarena.shared.util import gen_coord_space
from roboarena.shared.utils.vector import Vector

type Constraint = NDArray[np.bool_]  # 1d Vector containing the constraints (one hot)
type ConstraintSGrid = NDArray[
    np.bool_
]  # 2d grid with two dims representing the postion one hot values
type DirConstraint = dict[Vector[int], Constraint]
type ConstraintMap = dict[TileType, DirConstraint]
type ConstraintSlice = dict[Vector[int], bool]
type Tile = TileType
type Tiles = dict[Vector[int], Optional[Tile]]
#! TODO  type Tile = BasicTile

logger = logging.getLogger(f"{__name__}")

# @dataclass(frozen=True)
# class Vector[T]:
#     x: T
#     y: T


def convUcmCm(UCM: list[UserConstraint]) -> ConstraintMap:
    direction_to_vector: dict[Direction, Vector[int]] = {
        Direction.UP: Vector(0, -1),
        Direction.DOWN: Vector(0, 1),
        Direction.LEFT: Vector(-1, 0),
        Direction.RIGHT: Vector(1, 0),
    }

    inverse_direction: dict[Direction, Direction] = {
        Direction.UP: Direction.DOWN,
        Direction.DOWN: Direction.UP,
        Direction.LEFT: Direction.RIGHT,
        Direction.RIGHT: Direction.LEFT,
    }

    constraint_map: defaultdict[
        TileType, defaultdict[Vector[int], NDArray[np.bool_]]
    ] = defaultdict(
        lambda: defaultdict(lambda: np.zeros(len(TileType), dtype=np.bool_))
    )

    tile_type_to_index: dict[TileType, int] = {
        tile_type: index for index, tile_type in enumerate(TileType)
    }

    for uc in UCM:
        match uc:
            case UserConstraint(tt, constr):
                for direction, allowed_tile_types in constr.items():
                    pos = direction_to_vector[direction]
                    inv_pos = direction_to_vector[inverse_direction[direction]]
                    for att in allowed_tile_types:
                        constraint_map[tt][pos][tile_type_to_index[att]] = True
                        constraint_map[att][inv_pos][
                            tile_type_to_index[tt]
                        ] = True  # Adding inverse Constraint

    d = {k: dict(v) for k, v in constraint_map.items()}
    print(list(enumerate(TileType)))
    print(d)
    return d


def print_constraint_map(constraint_map: ConstraintMap, tile_types: list[TileType]):
    tile_type_to_index = {
        tile_type: index for index, tile_type in enumerate(tile_types)
    }
    index_to_tile_type = {
        index: tile_type for tile_type, index in tile_type_to_index.items()
    }

    for tile_type, directions in constraint_map.items():
        ir = {}
        for direction, constraints in directions.items():
            allowed_tiles = [
                index_to_tile_type[i].value
                for i, allowed in enumerate(constraints)
                if allowed
            ]
            ir[direction] = allowed_tiles

        print(tile_type, "\n", ir)


@dataclass
class WFC:
    tile_types: list[TileType]
    constraints: DirConstraint
    tiles: Tiles
    constraint_map: ConstraintMap
    not_collapsed: set[Vector[int]]
    uncollapsed: set[Vector[int]]

    @staticmethod
    def init_wfc(
        xsize: int,
        ysize: int,
        tile_types: list[TileType],
        constraint_map: ConstraintMap,
    ) -> "WFC":
        coords = gen_coord_space((0, xsize), (0, ysize))
        wfc = WFC(tile_types, {}, {}, deepcopy(constraint_map), set(), set())
        wfc.extend_level(coords)
        return wfc

    def extend_level(self, pos_list: list[Vector[int]]) -> bool:
        update = False
        for pos in pos_list:
            if pos in self.tiles:
                continue
            update = True
            self.constraints[pos] = np.ones(len(self.tile_types), dtype=np.bool_)
            self.tiles[pos] = None
            self.not_collapsed.add(pos)
            self.uncollapsed.add(pos)
        return update

    def print(self, sc: Optional[Vector[int]] = None):
        print_constraint_grid(self.constraints, self.tile_types, sc)
        # print_entropy_grid(self.constraints, self.tile_types, sc)
        print_grid(self.tiles)
        print(str("".join(["-" * 100])))

    def print2(self, sc: Optional[Vector[int]] = None):
        print_grid(self.tiles)
        print_constraint_grid(self.constraints, self.tile_types, sc)
        # print_entropy_grid(self.constraints, self.tile_types, sc)
        print(str("".join(["-" * 100])))

    # @log_durations(logger.critical, "slice: ", "ms")
    def slice_constraints(self, constr: DirConstraint) -> list[ConstraintSlice]:
        num_tile_types = len(self.tile_types)
        slices: list[ConstraintSlice] = [dict() for _ in range(num_tile_types)]

        for pos, constraint in constr.items():
            for k in range(num_tile_types):
                if constraint[k]:
                    slices[k][pos] = constraint[k]

        return slices

    # @log_durations(logger.critical, "implied: ", "ms")
    def implied_constraints(self, constr: Constraint) -> DirConstraint:
        num_tile_types = len(self.tile_types)
        implied_map: DirConstraint = {}
        constraint_map = deepcopy(self.constraint_map)

        for ti, val in enumerate(constr):
            if not val:
                continue

            tile_type = self.tile_types[ti]
            for neighbor_pos, neighbor_constraint in constraint_map[tile_type].items():
                if neighbor_pos not in implied_map:
                    implied_map[neighbor_pos] = np.zeros(num_tile_types, dtype=np.bool_)
                implied_map[neighbor_pos] |= neighbor_constraint

        return implied_map

    def propagte_constraints(self, positions: deque[Vector[int]]) -> None:
        while positions:
            pos = positions.popleft()
            implied_constraints = self.implied_constraints(self.constraints[pos])

            for dir, constr in implied_constraints.items():
                neighbor_pos = (pos + dir).floor()
                if neighbor_pos not in self.constraints:
                    self.constraints[neighbor_pos] = np.ones(
                        (len(self.tile_types),), dtype=np.bool_
                    )
                old_constraint = self.constraints[neighbor_pos].copy()
                self.constraints[neighbor_pos] &= constr
                if not np.array_equal(old_constraint, self.constraints[neighbor_pos]):
                    positions.append(neighbor_pos)

    def propagate_all_constraints(self) -> None:
        positions_to_propagate = deque(self.not_collapsed)
        self.propagte_constraints(positions_to_propagate)

    # @log_durations(logger.critical, "low_entropy: ", "ms")
    def low_entropy_tiles(
        self, entropy: Callable[[Constraint], float]
    ) -> tuple[list[Vector[int]], list[Vector[int]]]:
        entropy_map = {
            pos: entropy(constr)
            for pos, constr in self.constraints.items()
            if pos not in self.tiles or self.tiles[pos] is None
        }
        min_entropy = min(entropy_map.values())

        low_entropy_positions = [
            pos for pos, ent in entropy_map.items() if ent == min_entropy
        ]
        # logger.debug(f"{bcolors.WARNING}{self.tiles}{bcolors.ENDC}")
        existing_tiles = [
            pos
            for pos in low_entropy_positions
            if pos in self.tiles and self.tiles[pos] is None
        ]
        new_tiles = [pos for pos in low_entropy_positions if pos not in self.tiles]
        # logger.debug(
        #     f"{bcolors.FAIL}New:{new_tiles}\nExsist:{existing_tiles}{bcolors.ENDC}"
        # )
        return new_tiles, existing_tiles

    @log_durations(logger.critical, "collapse_map: ", "ms")
    def collapse_map(self) -> Tiles:
        def entropy(constraint: Constraint) -> float:
            return float(np.sum(constraint))
            probabilities = constraint / np.sum(constraint)
            return -np.sum(probabilities * np.log(probabilities + 1e-6))  # type: ignore

        i = 0
        while (
            any(tile is None for tile in self.tiles.values())
            and len(self.uncollapsed) > 0
        ):
            print(i)
            i += 1
            logger.error(f"{bcolors.FAIL}{'-'*100}{bcolors.ENDC}")
            # self.print()
            new_tiles, existing_tiles = self.low_entropy_tiles(entropy)
            # logger.debug(f"{bcolors.OKCYAN}{existing_tiles}\n{new_tiles}{bcolors.ENDC}")
            if len(existing_tiles) == 0:
                # logger.debug("new_tile")
                chosen_position = random.choice(new_tiles)
                self.tiles[chosen_position] = None
            else:
                # logger.debug("existing_tile")
                chosen_position = random.choice(existing_tiles)
            logger.critical(f"{chosen_position}")
            possible_tiles = self.constraints[chosen_position]
            if not possible_tiles.any():
                raise ValueError(
                    f"No valid tiles available for position {chosen_position}"
                )
            # logger.debug("-" * 100)
            # print(possible_tiles)
            chosen_tile = np.random.choice(np.flatnonzero(possible_tiles))

            self.tiles[chosen_position] = self.tile_types[chosen_tile]
            # print(
            #     chosen_position,
            #     "\n",
            #     chosen_tile,
            #     "\n",
            #     possible_tiles,
            #     "\n",
            #     self.tile_types,
            #     "\n",
            #     self.tiles[chosen_position],
            #     "\n",
            # )
            # print(self.tiles[chosen_position])

            self.constraints[chosen_position] = np.zeros_like(
                possible_tiles, dtype=np.bool_
            )
            self.constraints[chosen_position][chosen_tile] = True
            self.propagate_all_constraints()
            if chosen_position in self.not_collapsed:
                self.not_collapsed.remove(chosen_position)
                self.uncollapsed.remove(chosen_position)

            # self.print()
            new_t: Tiles = {}
            for di, c in self.constraints.items():
                if c.sum() == 1:
                    new_t[di] = one_hot_to_tiletype(c, self.tile_types)
            # if len(new_t) > 0:
            #     print(f"{bcolors.WARNING}")
            #     print_grid(new_t)
            #     print(f"{bcolors.ENDC}")
            # self.print2()
            # input()

        return self.tiles


def one_hot_to_tiletype(constraint: Constraint, tile_types: list[TileType]) -> TileType:
    tile_index = np.argmax(constraint)
    return tile_types[tile_index]


def get_grid(nodes: dict[Vector[int], Optional[Tile]]) -> list[list[str]]:
    return get_adaptive_grid(lambda x: str(x.value) if x else "*", nodes)
    min_x = min(coord.x for coord in nodes)
    max_x = max(coord.x for coord in nodes)
    min_y = min(coord.y for coord in nodes)
    max_y = max(coord.y for coord in nodes)

    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for coord, tile in nodes.items():
        if tile is not None:
            grid[coord.y - min_y][coord.x - min_x] = str(tile.value)

    return grid


def get_adaptive_grid[
    T
](
    f: Callable[[T], str],
    constraints: dict[Vector[int], T],
    special_coord: Optional[Vector[int]] = None,
) -> list[list[str]]:
    min_x = min(coord.x for coord in constraints)
    max_x = max(coord.x for coord in constraints)
    min_y = min(coord.y for coord in constraints)
    max_y = max(coord.y for coord in constraints)

    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for coord, constraint in constraints.items():

        grid[coord.y - min_y][coord.x - min_x] = f(constraint)
        if coord == Vector(0, 0):
            grid[coord.y - min_y][
                coord.x - min_x
            ] = f"{bcolors.OKGREEN}{grid[coord.y - min_y][coord.x - min_x]}{bcolors.ENDC}"
        if special_coord and special_coord == coord and False:  # ! Debug
            grid[coord.y - min_y][
                coord.x - min_x
            ] = f"{bcolors.WARNING}{grid[coord.y - min_y][coord.x - min_x]}{bcolors.ENDC}"

    return grid


def print_adaptive_grid[
    T
](
    f: Callable[
        [dict[Vector[int], T], list[TileType], Optional[Vector[int]]], list[list[str]]
    ],
    constraints: dict[Vector[int], T],
    tile_types: list[TileType],
    sc: Optional[Vector[int]] = None,
):
    grid = map(
        lambda x: x + "\n" + "#" * len(x),
        map(
            lambda x: "#".join(map(lambda x: str(x).ljust(len(tile_types)), x)),
            f(constraints, tile_types, sc),
        ),
    )
    print("\n".join(grid))


def get_constraint_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    special_coord: Optional[Vector[int]] = None,
) -> list[list[str]]:
    def f(constraint: Constraint) -> str:
        symbols = [tile_types[i].value for i, c in enumerate(constraint) if c]
        return "".join(symbols)

    return get_adaptive_grid(f, constraints, special_coord)


def print_constraint_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    sc: Optional[Vector[int]] = None,
):
    print_adaptive_grid(get_constraint_grid, constraints, tile_types, sc)


def get_entropy_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    special_coord: Optional[Vector[int]] = None,
) -> list[list[str]]:
    def f(constraint: Constraint) -> str:
        return f"{(constraint.sum())}"

    return get_adaptive_grid(f, constraints, special_coord)


def print_entropy_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    sc: Optional[Vector[int]] = None,
):
    print_adaptive_grid(get_entropy_grid, constraints, tile_types, sc)


def print_grid(nodes: dict[Vector[int], Optional[Tile]]):
    print("\n".join("".join(row) for row in get_grid(nodes)))


# Example usag
if __name__ == "__main__":
    # pass
    TL = list(x for x in TileType.__members__.values())
    cm = convUcmCm(UCM)
    print_constraint_map(cm, TL)
    s = 6
    wfc = WFC.init_wfc(s, s, TL, cm)
    c_pos = Vector(-1, -2)
    s = 1
    extend_dir = gen_coord_space((-s, s), (-s, s))
    wfc.print()
    wfc.collapse_map()
    wfc.print(c_pos)
    while True:
        tposs = [(c_pos + edir).floor() for edir in extend_dir]
        c_pos = (c_pos + Vector(0, 1)).floor()
        # wfc.print()
        wfc.extend_level(tposs)
        # print(wfc.tiles.keys(), c_pos)
        wfc.collapse_map()
        wfc.print(c_pos)
        input()
