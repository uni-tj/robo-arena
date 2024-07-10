import logging
import random
import sys
import time
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from functools import cache
from typing import Callable, Iterable, Optional

import numpy as np
from funcy import log_durations
from numpy.typing import NDArray

from roboarena.server.level_generation.level_config import UCM
from roboarena.server.level_generation.tile import TileType
from roboarena.server.level_generation.wfc import bcolors
from roboarena.shared.types import Direction, UserConstraint

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

logger = logging.getLogger(f"{__name__}")
# formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
fh = logging.FileHandler("spam.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
# stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
SEED = 100  # Seed 100 Produces a small map
random.seed(SEED)
np.random.seed(SEED)
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


type PropInfo = tuple[list[str], list[str], list[str], list[str]]
type ConstraintNum = int
type BoundValues = tuple[Vector[int], Vector[int]]


@dataclass(frozen=True)
class Boundaries:
    min: Vector[int]
    max: Vector[int]

    def extend(self, other: Vector[int]) -> "Boundaries":
        new_min = Vector(
            min(self.min.x, self.min.x + other.x), min(self.min.y, self.min.y + other.y)
        )
        new_max = Vector(
            max(self.max.x, self.max.x + other.x), max(self.max.y, self.max.y + other.y)
        )
        return Boundaries(new_min, new_max)

    def in_bounds(self, other: Vector[int]) -> bool:
        return not (other.any_geq(other) or other.any_leq(other))

    # def extend_symeticaly(self, size:)


def get_dict_bounds[T](d: dict[Vector[int], T]) -> Boundaries:
    positions = d.keys()
    return get_bounds(positions)


def get_bounds[T](positions: Iterable[Vector[int]]) -> Boundaries:
    max_x = max(positions, key=lambda x: x.x).x
    min_x = min(positions, key=lambda x: x.x).x
    max_y = max(positions, key=lambda x: x.y).y
    min_y = min(positions, key=lambda x: x.y).y
    return Boundaries(Vector(min_x, min_y), Vector(max_x, max_y))


@cache
def get_direction(size: int) -> list[Vector[int]]:
    return gen_coord_space((-size, size), (-size, size))


@cache
def sourround_directions(size: int, center: Vector[int]) -> list[Vector[int]]:
    return [(dir + center).round() for dir in get_direction(size)]


@dataclass
class WFC:
    tile_types: list[TileType]
    constraints: DirConstraint
    tiles: Tiles
    constraint_map: ConstraintMap
    not_collapsed: set[Vector[int]]
    all_updated: list[set[Vector[int]]]
    full_propagation: list[dict[Vector[int], dict[Vector[int], PropInfo]]]
    const_cache: dict[ConstraintNum, DirConstraint]
    # skip_expansion: Callable[["WFC", Vector[int]], bool]
    # tile_bounds: Boundaries = field(init=False)

    @staticmethod
    def init_wfc(
        xsize: int,
        ysize: int,
        tile_types: list[TileType],
        constraint_map: ConstraintMap,
    ) -> "WFC":
        coords = gen_coord_space((-xsize, xsize), (-ysize, ysize))

        wfc = WFC(
            tile_types,
            {},
            {},
            deepcopy(constraint_map),
            set(),
            [],
            [],
            {},
        )
        wfc.extend_level(coords)
        return wfc

    @staticmethod
    def constr_num(constaint: Constraint) -> ConstraintNum:
        return int(np.sum(2 ^ constaint))

    def gen_implied_constraints(self, constr: Constraint) -> DirConstraint:
        num_tile_types = len(self.tile_types)
        implied_map: DirConstraint = {}
        constraint_map = self.constraint_map

        for ti, val in enumerate(constr):
            if not val:
                continue

            tile_type = self.tile_types[ti]
            for neighbor_pos, neighbor_constraint in constraint_map[tile_type].items():
                if neighbor_pos not in implied_map:
                    implied_map[neighbor_pos] = np.zeros(num_tile_types, dtype=np.bool_)
                implied_map[neighbor_pos] |= neighbor_constraint

        return implied_map

    def get_implied_constraints(self, constraint: Constraint) -> DirConstraint:
        constr_num = self.constr_num(constraint)
        if constr_num not in self.const_cache:
            logger.debug("Cache miss")
            self.const_cache[constr_num] = self.gen_implied_constraints(constraint)
        return self.const_cache[constr_num]

    @staticmethod
    def get_neighbors(pos: Vector[int]) -> list[Vector[int]]:
        return [pos + dir for dir in [dir.value for dir in Direction]]

    def validate_contraint_map(self) -> Optional[Vector[int]]:
        for pos, allowed in self.constraints.items():
            allowed_by_neighbours = np.ones(len(self.tile_types), dtype=np.bool_)
            for dir in [dir.value for dir in Direction]:
                neighbour = pos + dir
                if neighbour not in self.constraints:
                    continue
                allowed_by_neighbour = np.zeros(len(self.tile_types), dtype=np.bool_)
                for neighbour_allowed_tile in conv_npconstraints(
                    self.constraints[neighbour], self.tile_types
                ):
                    allowed_by_neighbour |= self.constraint_map[neighbour_allowed_tile][
                        dir * (-1)
                    ]
                allowed_by_neighbours &= allowed_by_neighbour
            if not np.array_equal(allowed, allowed_by_neighbours):
                return pos
        return None

    def extend_level(self, pos_list: list[Vector[int]]) -> bool:
        update = False

        for pos in pos_list:
            if pos in self.tiles:
                continue
            positions = sourround_directions(
                len(self.tile_types) * 2,
                pos,
            )
            for sour in positions:
                if sour in self.constraints:
                    continue
                self.constraints[sour] = np.ones(len(self.tile_types), dtype=np.bool_)
                self.constraints[sour][0] = False
            self.tiles[pos] = None
            self.not_collapsed.add(pos)
            update = True
        self.tile_bounds = get_dict_bounds(self.tiles)
        return update

    def print(self, sc: Optional[dict[Vector[int], str]] = None):
        print_constraint_grid(self.constraints, self.tile_types, sc)
        print_grid(self.tiles)
        logger.debug(str("".join(["-" * 100])))

    def print2(self, sc: Optional[Vector[int]] = None):
        print_grid(self.tiles)
        print_constraint_grid(self.constraints, self.tile_types, sc)
        logger.debug(str("".join(["-" * 100])))

    # @log_durations(logger.debug, "slice: ", "ms")
    def slice_constraints(self, constr: DirConstraint) -> list[ConstraintSlice]:
        num_tile_types = len(self.tile_types)
        slices: list[ConstraintSlice] = [dict() for _ in range(num_tile_types)]

        for pos, constraint in constr.items():
            for k in range(num_tile_types):
                if constraint[k]:
                    slices[k][pos] = constraint[k]

        return slices

    def propagate_constraints(self, start_pos: Vector[int]) -> None:
        queue = deque([start_pos])
        self.all_updated.append(set())
        # self.full_propagation.append(defaultdict(lambda: dict()))
        while len(queue) > 0:
            pos = queue.popleft()
            # self.all_updated[-1].add(pos)
            # neighbour_allowed_by_pos = self.get_implied_constraints(
            #     self.constraints[pos]

            for dir in [dir.value for dir in Direction]:
                neighbour: Vector[int] = pos + dir  # type: ignore
                # if self.skip_expansion(self):
                #     continue
                if neighbour not in self.constraints:
                    continue
                    self.constraints[neighbour] = np.ones(
                        len(self.tile_types), dtype=np.bool_
                    )
                neighbour_allowed_by_pos = np.zeros(
                    (len(self.tile_types),), dtype=np.bool_
                )
                for tile_index, pos_is_allowed in enumerate(self.constraints[pos]):
                    if not pos_is_allowed:
                        continue
                    neighbour_allowed_by_pos |= self.constraint_map[
                        self.tile_types[tile_index]
                    ][dir]
                # if dir not in neighbour_allowed_by_pos:
                #     continue
                new_constraints = self.constraints[neighbour] & neighbour_allowed_by_pos
                new_constraints[0] = False
                # self.full_propagation[-1][pos][neighbour] = (
                #     conv_npconstraints_str(self.constraints[pos], self.tile_types),
                #     conv_npconstraints_str(
                #         self.constraints[neighbour], self.tile_types
                #     ),
                #     conv_npconstraints_str(neighbour_allowed_by_pos, self.tile_types),
                #     conv_npconstraints_str(new_constraints, self.tile_types),
                # )
                if np.sum(self.constraints[neighbour]) == np.sum(new_constraints):
                    continue
                self.constraints[neighbour] = new_constraints
                self.all_updated[-1].add(neighbour)
                queue.append(neighbour)

    # @log_durations(logger.debug, "low_entropy: ", "ms")
    def low_entropy_tiles(
        self, entropy: Callable[[Constraint], float]
    ) -> list[Vector[int]]:
        # tuple[list[Vector[int]], list[Vector[int]]]:
        entropy_map_new: dict[float, list[Vector[int]]] = defaultdict(lambda: list())
        entropy_map_old: dict[float, list[Vector[int]]] = defaultdict(lambda: list())
        min_entropy = float("inf")

        for pos, constr in self.constraints.items():
            if pos not in self.tiles or self.tiles[pos] is None:
                ent = entropy(constr)
                if ent > min_entropy:
                    continue
                if ent < min_entropy:
                    min_entropy = ent
                if pos in self.tiles:
                    entropy_map_old[ent].append(pos)
                else:
                    entropy_map_new[ent].append(pos)
        if len(entropy_map_old[min_entropy]) > 0:
            return entropy_map_old[min_entropy]
        else:
            return entropy_map_new[min_entropy]

    def get_steps_with_last_index(
        self, checking: Vector[int]
    ) -> list[tuple[Vector[int], Vector[int], PropInfo]]:
        result = []

        for propagation_dict in self.full_propagation:
            for start_vector, inner_dict in propagation_dict.items():
                for end_vector, (
                    original_c,
                    pos_c,
                    actions,
                    conditions,
                ) in inner_dict.items():
                    if end_vector == checking:
                        result.append(
                            (
                                start_vector,
                                end_vector,
                                (original_c, pos_c, actions, conditions),
                            )
                        )

        return result

    @log_durations(logger.critical, "collapse_map: ", "ms")
    def collapse_map(self) -> Tiles:
        def entropy(constraint: Constraint) -> float:
            return float(np.sum(constraint))
            probabilities = constraint / np.sum(constraint)
            return -np.sum(probabilities * np.log(probabilities + 1e-6))  # type: ignore

        i = 0
        timings: defaultdict[str, float] = defaultdict(lambda: 0)
        while (
            # any(tile is None for tile in self.tiles.values())
            # and
            len(self.not_collapsed)
            > 0
        ):
            i += 1
            t0 = time.time()
            chosen_positions = self.low_entropy_tiles(entropy)
            chosen_positions = [chosen_positions[0]]
            timings["entropy"] += time.time() - t0
            for chosen_position in chosen_positions:
                t0 = time.time()
                self.tiles[chosen_position] = None
                timings["chose"] += time.time() - t0

                possible_tiles = self.constraints[chosen_position].copy()
                possible_tiles[0] = False
                if np.sum(possible_tiles) == 0:
                    chosen_tile = 0
                else:
                    chosen_tile = np.random.choice(np.flatnonzero(possible_tiles))

                self.tiles[chosen_position] = self.tile_types[chosen_tile]

                self.constraints[chosen_position] = np.zeros_like(
                    possible_tiles, dtype=np.bool_
                )
                self.constraints[chosen_position][chosen_tile] = True

                t0 = time.time()
                self.propagate_constraints(chosen_position)
                timings["prop"] += time.time() - t0

                if chosen_position in self.not_collapsed:
                    self.not_collapsed.remove(chosen_position)

        return self.tiles


def one_hot_to_tiletype(constraint: Constraint, tile_types: list[TileType]) -> TileType:
    tile_index = np.argmax(constraint)
    return tile_types[tile_index]


def conv_npconstraints(
    constraint: Constraint, tile_types: list[TileType]
) -> list[TileType]:
    return [tile_types[i] for i, c in enumerate(constraint) if c]


def conv_npconstraints_str(
    constraint: Constraint, tile_types: list[TileType]
) -> list[str]:
    return [tile_types[i].value for i, c in enumerate(constraint) if c]


def conv_propagationconstr_str(
    constraint: tuple[Constraint, Constraint], tile_types: list[TileType]
) -> tuple[list[str], list[str]]:
    match constraint:
        case (np_1, np_2):
            return (
                conv_npconstraints_str(np_1, tile_types),
                conv_npconstraints_str(np_2, tile_types),
            )


def get_grid(nodes: dict[Vector[int], Optional[Tile]]) -> list[list[str]]:
    return get_adaptive_grid(lambda x: str(x.value) if x else "*", nodes, pad=0)
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
    special_coord: Optional[dict[Vector[int], str]] = None,
    pad: int = 10,
) -> list[list[str]]:
    min_x = min(coord.x for coord in constraints)
    max_x = max(coord.x for coord in constraints)
    min_y = min(coord.y for coord in constraints)
    max_y = max(coord.y for coord in constraints)

    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for coord, constraint in constraints.items():

        grid[coord.y - min_y][coord.x - min_x] = f(constraint).ljust(pad)
        c_str = grid[coord.y - min_y][coord.x - min_x]
        if coord == Vector(0, 0):
            grid[coord.y - min_y][
                coord.x - min_x
            ] = f"{bcolors.OKGREEN}{c_str}{bcolors.ENDC}"
        if special_coord and coord in special_coord.keys():  # ! Debug
            grid[coord.y - min_y][
                coord.x - min_x
            ] = f"{special_coord[coord]}{c_str}{bcolors.ENDC}"

    return grid


def print_tile_grid[
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
            lambda x: "#".join(map(lambda x: str(x).ljust(1), x)),
            f(constraints, tile_types, sc),
        ),
    )
    print("\n".join(grid))


def print_adaptive_grid[
    T
](
    f: Callable[
        [dict[Vector[int], T], list[TileType]],
        list[list[str]],
    ],
    constraints: dict[Vector[int], T],
    tile_types: list[TileType],
    sc: Optional[dict[Vector[int], str]] = None,
):
    grid = map(
        lambda x: x + "\n" + "#" * len(x),
        map(
            lambda x: "#".join(map(lambda x: str(x).ljust(10), x)),
            f(constraints, tile_types),
        ),
    )
    logger.debug("\n".join(grid))


def get_constraint_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    special_coord: Optional[dict[Vector[int], str]] = None,
) -> list[list[str]]:
    def f(constraint: Constraint) -> str:
        symbols = [tile_types[i].value for i, c in enumerate(constraint) if c]
        return "".join(symbols)

    return get_adaptive_grid(f, constraints, special_coord)


def print_constraint_grid(
    constraints: dict[Vector[int], Constraint],
    tile_types: list[TileType],
    sc: Optional[dict[Vector[int], str]] = None,
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
    logger.debug("\n".join("".join(row) for row in get_grid(nodes)))


# Example usag
if __name__ == "__main__":
    # pass
    TL = list(x for x in TileType.__members__.values())
    cm = convUcmCm(UCM)
    print_constraint_map(cm, TL)
    s = 1
    wfc = WFC.init_wfc(s, s, TL, cm)
    c_pos = Vector(-1, -2)
    s = 3
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
        # time.sleep(1)
