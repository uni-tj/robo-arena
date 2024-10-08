import logging
import math
import random
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from functools import cache
from math import ceil, sqrt
from typing import Iterable, Sequence

from attr import define, field

from roboarena.server.level_generation.utils import gen_square_space_wfc_fast
from roboarena.shared.types import (
    PossibleTiles,
    Tile,
    TilePosition,
    Ts,
    WFCMap,
    WFCUpdate,
)
from roboarena.shared.util import (
    Color,
    EventTarget,
    color,
    is_one_at,
    nonzero,
    nonzero_count,
    nonzero_inv,
    one_hot,
    ones_except,
)
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(__file__)
# logger = logging.Logger("wfc")
# fh = logging.FileHandler("wfc.log")
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)
# stdout_handler = logging.StreamHandler(sys.stdout)

# stdout_handler.setLevel(logging.DEBUG)
# logger.addHandler(stdout_handler)

# seed = 24
# np.random.seed(seed)
# random.seed(seed)

# Wave Function Collapse implementation


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

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other


entropy = nonzero_count


@dataclass(frozen=True)
class CollapsedOneEvent:
    position: TilePosition


@dataclass(frozen=True)
class CollapsedAllEvent:
    positions: Sequence[TilePosition]


@dataclass(frozen=True)
class PropagatedOneEvent:
    position: TilePosition


def print_trace() -> None:
    try:
        raise Exception("")
    except Exception:
        print(traceback.format_exc())
        traceback.print_exc()


@define
class MinEntropyStore:
    _entropies: dict[int, set[TilePosition]] = field(factory=lambda: defaultdict(set))
    """
    Invariant: Untion of all values is subset of not_collapsed

    Positions are added initially and updated when changed by propagation.
    Positions are removed when they are collapsed.
    Used for speeding up the computations of wfc
    """

    def add(self, position: TilePosition, entropy: int) -> None:
        self._entropies[entropy].add(position)

    def update(self, position: TilePosition, old_entropy: int, new_entropy: int):
        self._entropies[old_entropy].remove(position)
        self._entropies[new_entropy].add(position)

    def pop_min(self) -> TilePosition:
        for _, ps in sorted(self._entropies.items(), key=lambda _: _[0]):
            if len(ps) == 0:
                continue
            selected = random.choice(tuple(ps))
            ps.remove(selected)
            return selected
        raise Exception("Cannot pop from Empty store.")

    def _all_positions(self) -> set[TilePosition]:
        all: set[TilePosition] = set()
        for ps in self._entropies.values():
            assert all.intersection(ps) == set()
            all = all.union(ps)
        return all

    def __contains__(self, position: TilePosition) -> bool:
        return position in self._all_positions()


@define
class WFC:
    tileset: Tileset
    map: WFCMap = field(init=False, factory=dict)
    events: EventTarget[CollapsedOneEvent | CollapsedAllEvent | PropagatedOneEvent] = (
        field(init=False, factory=EventTarget)
    )

    # Performance relevant
    _collapsed: set[TilePosition] = field(init=False, factory=set)
    _not_collapsed: set[TilePosition] = field(init=False, factory=set)
    _args: set[TilePosition] = field(init=False, factory=set)
    """Positions explicitly requested as arguments to `collapse`."""
    _entropy_store: MinEntropyStore = field(init=False, factory=MinEntropyStore)

    @staticmethod
    def from_map(tileset: Tileset, map: dict[TilePosition, Tile]) -> "WFC":
        """Initializes a WFC instance where tiles are placed according to the map"""
        wfc = WFC(tileset)
        for p, t in map.items():
            wfc.map[p] = one_hot(t)
            wfc._not_collapsed.add(p)
            wfc._entropy_store.add(p, 1)
        return wfc

    def collapse(self, positions: Iterable[TilePosition]) -> WFCUpdate:
        """Guarantee positions to be collapsed and return newly collapsed"""
        positions = set(positions)
        positions = positions.difference(self._args)  # already handled before
        # _args contain the positions that were already passed as arguments
        self._args = self._args.union(positions)

        # calculate the values that need to be placed on map expansions
        init_possible = ones_except(self.tileset.tiles, 0)
        init_entropy = entropy(init_possible)

        # Initialization of new positions into the map
        alloc_apothem = ceil(4 * math.log(self.tileset.tiles, 2))  # works empirically
        for pos in positions:
            for sur in gen_square_space_wfc_fast(pos, alloc_apothem):
                if sur in self.map:
                    continue
                self.map[sur] = init_possible
                self._not_collapsed.add(sur)
                self._entropy_store.add(sur, init_entropy)

        # Collapse
        map_update: WFCUpdate = list()
        positions = positions.difference(self._collapsed)
        while len(positions) > 0:
            # select tile with lowest entropy
            pos = self._entropy_store.pop_min()
            # select random tiletype from the possible tiletypes
            selected = self._select_possible(self.map[pos])
            # Update the map with the selected tile
            self.map[pos] = one_hot(selected)

            # If we select the impossible tile we dont want to propagate theinformation
            if selected != 0:
                self._propagate(pos)

            # Update all tracking variables
            self._collapsed.add(pos)
            self._not_collapsed.remove(pos)
            positions.discard(pos)
            self._collapsed.add(pos)
            # Add the selection to the map update
            map_update.append((pos, selected))

            # DEBUG dispach a Event for testing
            self.events.dispatch(CollapsedOneEvent(pos))
        # DEBUG dispach a Event for testing
        self.events.dispatch(CollapsedAllEvent(list(p for p, _ in map_update)))
        return map_update

    def _select_possible(self, possible: PossibleTiles) -> Tile:
        if possible == 0:
            return 0
        return random.choice(nonzero(possible))

    def _propagate(self, start: TilePosition) -> None:
        """Propagates the update of one position(tile selection)
        to all tiles until no more updates occur
        Args:
            start (TilePosition): The position that was changed in the map

        """
        ts = self.tileset
        queue = deque([start])
        while len(queue) > 0:
            pos = queue.popleft()
            if self.map[pos] == 0:
                continue  # nothing possible
            # Update the constraints of all neighbours
            for dir in Direction:
                neigh = pos + dir.value
                if neigh not in self.map:
                    continue
                old = self.map[neigh]
                # Use Binary and to remove all possiblities,
                # that are not in the neighbour and implied constraints.
                self.map[neigh] &= self._propagation_by_poss(self.map[pos], dir, ts)
                new = self.map[neigh]
                # If the map for the neighbor wasnt changed the neighbour cannot
                # propagate any new information to its neighbors
                if old != new:
                    if neigh not in self._not_collapsed:
                        continue
                    self._entropy_store.update(neigh, entropy(old), entropy(new))
                    queue.append(neigh)

            # DEBUG dispach a Event for testing
            self.events.dispatch(PropagatedOneEvent(pos))

    @staticmethod
    @cache
    def _propagation_by_poss(
        tiles: PossibleTiles, dir: Direction, ts: Ts
    ) -> PossibleTiles:
        """_propagate helper. Get possible neighbours for all possible tiles"""
        prop = 0
        for tile in nonzero(tiles):
            prop |= WFC._propagation_by_tile(tile, dir, ts)
        return prop

    @staticmethod
    @cache
    def _propagation_by_tile(tile: Tile, dir: Direction, ts: Ts) -> PossibleTiles:
        """_propagate helper. Get possible neighbours for one tile"""
        rules = ts.rules_horiz if dir.is_horizontal() else ts.rules_vert
        index = 0 if dir.is_bottom_right() else 1
        return nonzero_inv(rule[1 - index] for rule in rules if rule[index] == tile) | 1


def print_wfc(
    wfc: WFC,
    tiles: dict[int, str | None] = {},  # noqa: B006
    colors: dict[TilePosition, Color] = {},  # noqa: B006
):
    """Prints the WFC onto the screen in a grid for ease of inspection

    Args:
        wfc (WFC): _description_
        tiles : A map containg string names for each tile. Defaults to {}.
        colors (dict[Tileposition| Color], optional):
        Tiles that should be colored in a certain way. Defaults to {}.
    """
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
                poss = tile < wfc.tileset.tiles and is_one_at(possible, tile)
                char_pos = char_tile_pos + Vector(x, y)
                c = colors.get(tile_pos) or Color.NONE
                str = (tiles.get(tile) or f"{tile}") if poss else " "
                matrix[char_pos.y][char_pos.x] = color(str, c)

    logger.critical("\n".join(["".join(row) for row in matrix]))
