import logging
import random
import sys
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from functools import cache, cached_property
from itertools import chain
from math import ceil, sqrt
from random import choice
from typing import Iterable, Sequence, SupportsIndex

import numpy as np
from attr import define, field
from numpy.typing import NDArray

from roboarena.shared.util import Color, EventTarget, color, square_space_around
from roboarena.shared.utils.vector import Vector

# logger = logging.getLogger(__file__)
logger = logging.Logger("wfc")
fh = logging.FileHandler("wfc.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)

seed = 24
np.random.seed(seed)
random.seed(seed)

# General purpose helpers

type ShapeLike = SupportsIndex | Sequence[SupportsIndex]


def flatnonzero_inv(indices: Iterable[int], shape: ShapeLike) -> NDArray[np.bool_]:
    arr = np.zeros(shape, dtype=np.bool_)
    flat_view = arr.ravel()
    for index in indices:
        flat_view[index] = True
    return arr


# Wave Function Collapse implementation

type Tile = int
type TilePosition = Vector[int]
type PossibleTiles = NDArray[np.bool_]
type WFCMap = dict[TilePosition, PossibleTiles]
type WFCUpdate = Iterable[tuple[TilePosition, int]]


class Direction(Enum):
    UP = Vector[int](0, -1)
    DOWN = Vector[int](0, 1)
    LEFT = Vector[int](-1, 0)
    RIGHT = Vector[int](1, 0)

    def is_horizontal(self):
        return self.value.y == 0

    def is_bottom_right(self):
        return self.value.x >= 0 and self.value.y >= 0


@dataclass(frozen=True)
class Tileset:
    tiles: int
    """Tiles. First element must be the fallback tile"""
    rules_horiz: frozenset[tuple[Tile, Tile]]
    """Possible horizontal patterns as (left, right)"""
    rules_vert: frozenset[tuple[Tile, Tile]]
    """Possible vertical patterns as (top, bottom)"""

    @staticmethod
    def validate(ts: "Tileset") -> None:
        assert ts.tiles >= 1, "Empty tiles. At least a fallback tiles required."


type Ts = Tileset


def one_hot(value: int, classes: int) -> NDArray[np.bool_]:
    arr = np.zeros((classes,), np.bool_)
    arr[value] = True
    return arr


def entropy(possible: PossibleTiles) -> int:
    return possible.sum()


@define
class Tank:
    mileage: int = field(default=0, init=False)
    reach: int

    def use(self) -> None:
        self.mileage += 1
        logger.critical(f"mileage: {self.mileage}")
        if self.mileage >= self.reach:
            raise Exception("Out of fuel.")


tank = Tank(309)
tank2 = Tank(119)


@dataclass(frozen=True)
class CollapsedOneEvent:
    position: TilePosition


@dataclass(frozen=True)
class CollapsedAllEvent:
    positions: Sequence[TilePosition]


@dataclass(frozen=True)
class PropagatedOneEvent:
    position: TilePosition


@define
class WFC:
    tileset: Tileset
    map: WFCMap = field(init=False, factory=dict)
    collapsed: set[TilePosition] = field(init=False, factory=set)
    not_collapsed: set[TilePosition] = field(init=False, factory=set)
    events: EventTarget[CollapsedOneEvent | CollapsedAllEvent | PropagatedOneEvent] = (
        field(init=False, factory=EventTarget)
    )

    def collapse(self, positions: Iterable[TilePosition]) -> WFCUpdate:
        """Guarantee positions to be collapsed and return newly collapsed"""
        positions = set(positions)
        init_possible = np.ones(self.tileset.tiles, dtype=np.bool_)
        init_possible[0] = False
        alloc_apothem = 2 * self.tileset.tiles  # works empirically
        for pos in positions:
            for sur in square_space_around(pos, alloc_apothem):
                if sur in self.map:
                    continue
                self.map[sur] = init_possible.copy()
                self.not_collapsed.add(sur)
        # print(self.map)
        positions -= self.collapsed
        map_update: WFCUpdate = list()
        while len(positions) > 0:
            # collapse tile with lowest entropy
            pos = self._lowest_entropy_position()
            selected = self._select_possible(self.map[pos])
            self.map[pos] = one_hot(selected, self.tileset.tiles)
            if selected != 0:
                self._propagate(pos)
            self.collapsed.add(pos)
            self.not_collapsed.remove(pos)
            positions.discard(pos)
            map_update.append((pos, selected))
            # logger.critical(f"collapsed: {pos}, selected: {selected}")
            # self.print(pos)
            # input()
            # tank.use()
            self.events.dispatch(CollapsedOneEvent(pos))
        self.events.dispatch(CollapsedAllEvent(list(p for p, _ in map_update)))
        return map_update

    def _lowest_entropy_position(self) -> TilePosition:
        not_collapsed = deepcopy(self.not_collapsed)
        min_entropy = min(map(lambda p: entropy(self.map[p]), not_collapsed))
        min_poss = filter(lambda p: entropy(self.map[p]) == min_entropy, not_collapsed)
        return choice(list(min_poss))

    def _select_possible(self, possible: PossibleTiles) -> Tile:
        if np.sum(possible) == 0:
            return 0
        return np.random.choice(np.flatnonzero(possible))

    def _propagate(self, start: TilePosition) -> None:
        queue = deque([start])
        while len(queue) > 0:
            pos = queue.popleft()
            if np.array_equal(self.zeros, self.map[pos]):
                continue
            for dir in Direction:
                neigh = pos + dir.value
                if neigh not in self.map:
                    continue
                before = self.map[neigh].copy()
                possible = frozenset(np.flatnonzero(self.map[pos]))
                ts = self.tileset
                self.map[neigh] &= self._propagation_by_poss(possible, dir, ts)
                assert before.sum() >= self.map[neigh].sum()
                no_change = np.array_equal(before, self.map[neigh])
                if not no_change:
                    queue.append(neigh)
            self.events.dispatch(PropagatedOneEvent(pos))

    @staticmethod
    @cache
    def _propagation_by_poss(tiles: set[Tile], dir: Direction, ts: Ts) -> PossibleTiles:
        """_propagate helper. Get possible neighbours for all possible tiles"""
        prop = np.zeros((ts.tiles,), dtype=np.bool_)
        for tile in tiles:
            prop |= WFC._propagation_by_tile(tile, dir, ts)
        return prop

    @staticmethod
    @cache
    def _propagation_by_tile(tile: Tile, dir: Direction, ts: Ts) -> PossibleTiles:
        """_propagate helper. Get possible neighbours for one tile"""
        rules = ts.rules_horiz if dir.is_horizontal() else ts.rules_vert
        index = 0 if dir.is_bottom_right() else 1
        return flatnonzero_inv(
            chain([0], (rule[1 - index] for rule in rules if rule[index] == tile)),
            (ts.tiles,),
        )

    @cached_property
    def zeros(self) -> NDArray[np.bool_]:
        return np.zeros((self.tileset.tiles,), dtype=np.bool_)


def print_wfc(
    wfc: WFC,
    tiles: dict[int, str | None] = {},  # noqa: B006
    colors: dict[TilePosition, Color] = {},  # noqa: B006
):
    min_pos = Vector(min(p.x for p in wfc.map), min(p.y for p in wfc.map))
    max_pos = Vector(max(p.x for p in wfc.map), max(p.y for p in wfc.map))
    dim = max_pos - min_pos + 1
    tile_size = ceil(sqrt(wfc.tileset.tiles))
    char_dim = dim * (tile_size + 1) + 1

    # fill screen with divider
    matrix = [["#" for _ in range(char_dim.x)] for _ in range(char_dim.y)]
    # print possibilities
    for tile_pos, possible in wfc.map.items():
        char_tile_pos = (tile_pos - min_pos) * (tile_size + 1) + 1
        for x in range(tile_size):
            for y in range(tile_size):
                tile = y * tile_size + x
                poss = tile < len(possible) and possible[tile]
                char_pos = char_tile_pos + Vector(x, y)
                c = colors.get(tile_pos) or Color.NONE
                str = (tiles.get(tile) or f"{tile}") if poss else " "
                matrix[char_pos.y][char_pos.x] = color(str, c)

    logger.critical("\n".join(["".join(row) for row in matrix]))
