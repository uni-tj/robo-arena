import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional

import numpy as np


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(
        self,
        o: "Position",
    ) -> "Position":
        return Position(self.x + o.x, self.y + o.y)

    def __mul__(
        self,
        o: "Position",
    ) -> "Position":
        return Position(self.x * o.x, self.y * o.y)

    def __sub__(
        self,
        o: "Position",
    ) -> "Position":
        return Position(self.x - o.x, self.y - o.y)

    def apply_transform(self, f: Callable[[int], int] = lambda x: x):
        return Position(f(self.x), f(self.y))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Position):
            return NotImplemented
        return (self.x - o.x, self.y - o.y) == (0, 0)

    def tuple_repr(self) -> tuple[int, int]:
        return (self.x, self.y)

    def drawing_coords(self, size: int) -> tuple[int, int, int, int]:
        return self.x * size, self.y * size, size, size

    def dot_product(self, o: "Position") -> int:
        return self.x * o.x + self.y * o.y

    @staticmethod
    def random_pos(mx: int, my: int) -> "Position":
        return Position(random.randint(0, mx - 1), random.randint(0, my - 1))


@dataclass
class Edge[L, T]:
    edgeval: L
    target: T


@dataclass
class Collapsable[C, N]:
    # neighbors: dict[
    #     P, list[P]
    # ]  # it is possible to remove this due to the rules of tiles which dictate which tiles are neighbored (allowing for more complex neighboring )
    constraints: dict[Position, set[C]]
    nodes: dict[Position, Optional[N]]

    def print_constraints(self):
        print_constraint_grid(self.constraints)

    def print_nodes(self):
        print_grid(self.nodes)


def get_grid(nodes: dict[Position, Optional["Tile"]]):
    """Returns a grid-like representation of the nodes, arranged by their (x, y) positions."""
    position = nodes
    max_x = max(position, key=lambda x: x.x).x
    min_x = min(position, key=lambda x: x.x).x
    max_y = max(position, key=lambda x: x.y).y
    min_y = min(position, key=lambda x: x.y).y
    # Create a grid, initially filled with None
    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    # Place nodes in their positions
    for position, cons in nodes.items():
        x, y = position.tuple_repr()
        grid[y - min_y][x - min_x] = str(cons) if cons is not None else "⑔"
    return grid


def get_constraint_grid(constraints: dict[Position, set["TileType"]]):
    """Returns a grid-like representation of the nodes, arranged by their (x, y) positions."""
    position = constraints
    max_x = max(position, key=lambda x: x.x).x
    min_x = min(position, key=lambda x: x.x).x
    max_y = max(position, key=lambda x: x.y).y
    min_y = min(position, key=lambda x: x.y).y
    # Create a grid, initially filled with None
    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    # Place nodes in their positions
    for position, cons in constraints.items():
        x, y = position.tuple_repr()
        ns = "".join(map(lambda x: x.name, cons))
        grid[y - min_y][x - min_x] = ns
    return grid


def print_grid(nodes: dict[Position, Optional["Tile"]]):
    print("\n".join(map(lambda x: "".join(x), get_grid(nodes))))


def print_constraint_grid(constraints: dict[Position, set["TileType"]]):
    grid = map(
        lambda x: x + "\n" + "-" * len(x),
        map(
            lambda x: "|".join(map(lambda x: str(x).ljust(10), x)),
            get_constraint_grid(constraints),
        ),
    )
    print("\n".join(grid))


@dataclass
class Tile:
    color: str
    type: "TileType"

    def __str__(self) -> str:
        return self.color


class TileType(Enum):
    # R = "R"
    # B = "B"
    # C = "C"
    H = "─"
    V = "|"
    C = "┼"
    E = "├"
    EI = "┤"
    TI = "┴"
    T = "┬"
    # # N = "N"
    # UL = "UL"
    # UR = "UR"
    # BL = "BL"
    # BR = "BR"


# Box Drawing (U+2500 to U+257F) https://www.vertex42.com/ExcelTips/unicode-symbols.html#number-forms
# Switching from the user specified Constraint map to a less error prone variant that is not directional
class Direction(Enum):
    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)


@dataclass(frozen=True)
class UserConstraint:
    direction: list[Direction]
    tt: TileType
    tiles: list[TileType]


UserConstraintList = list[UserConstraint]
# ucm = [
#     UserConstraint([Direction.RIGHT], TileType.UL, [TileType.UR]),
#     UserConstraint([Direction.LEFT], TileType.UL, [TileType.UR]),
#     UserConstraint([Direction.UP], TileType.UL, [TileType.BL]),
#     UserConstraint([Direction.DOWN], TileType.UL, [TileType.BL]),
#     UserConstraint([Direction.RIGHT, Direction.LEFT], TileType.BL, [TileType.BR]),
#     UserConstraint([Direction.UP, Direction.DOWN], TileType.BR, [TileType.UR]),
# ]

ucm = [
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
        [Direction.LEFT, Direction.RIGHT],
        TileType.H,
        [TileType.H, TileType.T, TileType.TI, TileType.C],
    ),
    UserConstraint(
        [Direction.UP, Direction.DOWN],
        TileType.V,
        [TileType.V, TileType.E, TileType.EI, TileType.C],
    ),
]

ucm = [
    UserConstraint(
        [Direction.RIGHT, Direction.LEFT],
        TileType.H,
        [TileType.H, TileType.C, TileType.E, TileType.EI, TileType.T, TileType.TI],
    ),
    UserConstraint(
        [Direction.UP, Direction.DOWN],
        TileType.V,
        [TileType.V, TileType.C, TileType.E, TileType.EI, TileType.T, TileType.TI],
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
        [TileType.H, TileType.C, TileType.E, TileType.EI, TileType.V, TileType.TI],
    ),
    UserConstraint(
        [Direction.RIGHT, Direction.LEFT, Direction.UP],
        TileType.TI,
        [TileType.H, TileType.C, TileType.E, TileType.EI, TileType.V, TileType.T],
    ),
]
Constraint = dict[Position, set[TileType]]
ConstraintMap = dict[TileType, Constraint]


def generate_constraint_map(ucm: UserConstraintList) -> ConstraintMap:
    cm: ConstraintMap = {}
    for const in ucm:
        match const:
            case UserConstraint(dirs, tt, tiles):
                for dir in dirs:
                    if tt not in cm:
                        cm[tt] = {}
                    if dir.value not in cm[tt]:
                        cm[tt][dir.value] = set()
                    cm[tt][dir.value] = cm[tt][dir.value].union(set(tiles))
                    for ntt in tiles:
                        if ntt not in cm:
                            cm[ntt] = {}
                        idir = dir.value * Position(-1, -1)
                        if idir not in cm[ntt]:
                            cm[ntt][idir] = set()
                        cm[ntt][idir] = cm[ntt][idir].union(set([tt]))
    return cm


def pos2dir(pos: Position) -> Direction:
    match pos:
        case Position(0, -1):
            return Direction.UP
        case Position(0, 1):
            return Direction.DOWN
        case Position(-1, 0):
            return Direction.LEFT
        case Position(1, 0):
            return Direction.RIGHT
        case _:
            raise Exception(f"Invalid direction: {pos}")


TL = set(x for x in TileType.__members__.values())
WFCCollapsble = Collapsable[TileType, Tile]


def get_collapsable(tg: WFCCollapsble) -> Optional[Position]:
    collapseable: dict[int, list[Position]] = {}
    min_constr = len(TL) + 1

    for pos, node in tg.nodes.items():
        if node is not None:
            continue

        num_constraints = len(tg.constraints[pos])
        if num_constraints < min_constr:
            min_constr = num_constraints
            collapseable = {min_constr: [pos]}
        elif num_constraints == min_constr:
            collapseable[min_constr].append(pos)

    if len(collapseable) == 0:
        return None

    return random.choice(collapseable[min_constr])


def construct_Tile(tt: TileType):
    return Tile(tt.value, tt)
    # TODO Example


def wave_function_collapse(
    tg: WFCCollapsble,
    end_pred: Callable[[WFCCollapsble], bool],
    consttraint_map: ConstraintMap,
):
    selected_tile = get_collapsable(tg)
    print(consttraint_map)
    # Update Constraint map for items that are None
    for type, cons in consttraint_map.items():
        new_dict: Constraint = {}
        for dir, constraint in cons.items():
            new_dict[dir] = constraint
            consttraint_map[type] = new_dict
    while selected_tile is not None and not end_pred(tg):
        pos_tiles: set[TileType] = tg.constraints[selected_tile]
        print(list(map(lambda x: x.name, pos_tiles)))
        selected_type = random.choice(list(pos_tiles))
        cons = consttraint_map[selected_type]
        print(selected_tile, selected_type)
        propagate(tg, selected_tile, selected_type, consttraint_map)
        tg.print_nodes()
        tg.print_constraints()
        selected_tile = get_collapsable(tg)


def propagate(
    tg: WFCCollapsble, pos: Position, tt: TileType, constraints: ConstraintMap
) -> None:
    # ! Mutates the tg WFCCollapsble in place
    tg.constraints[pos] = set([tt])
    tg.nodes[pos] = construct_Tile(tt)
    print(tg.nodes[pos], pos)
    old_map = tg.constraints
    print("." * 100)
    tg.print_constraints()
    tg.print_nodes()
    new_map = {}
    while new_map != old_map:
        res = update_map(
            old_map, tg.nodes, constraints, generate_neighbors_map(constraints)
        )
        if new_map != {}:
            old_map = new_map

        new_map = res
    print(bcolors.FAIL + "Finsihed iteration" + bcolors.ENDC)
    tg.constraints = new_map
    tg.print_constraints()


neighbors_map = list[tuple[TileType, Position]]


def calculate_neighbors(
    map: dict[Position, set[TileType]], pos: Position, cm: neighbors_map
) -> list[tuple[TileType, Position, Position]]:
    # The Neighborsmap can be computed once on start
    nl: list[tuple[TileType, Position, Position]] = []
    for ntt, dir in cm:
        npos = pos - dir
        if npos not in map:
            continue
        if ntt in map[npos]:
            nl.append((ntt, npos, dir))
    return nl


def generate_neighbors_map(cm: ConstraintMap) -> neighbors_map:
    res: neighbors_map = []
    for ntt, consts in cm.items():
        for dir, _ in consts.items():
            res.append((ntt, dir))
    return res


def propagate_neighbors(
    cmap: dict[Position, set[TileType]],
    pos: Position,
    cm: ConstraintMap,
    nm: neighbors_map,
) -> set[TileType]:
    curr_tt = TL
    nl: list[tuple[TileType, Position, Position]] = calculate_neighbors(cmap, pos, nm)
    nttm: dict[Position, set[TileType]] = {}
    print("_" * 32)
    print(pos)
    for ntt, npos, ndir in nl:
        if ntt not in cmap[npos]:
            continue
        cos_tt = cm[ntt][ndir]
        if npos not in nttm:
            nttm[npos] = set()
        print("ox1", npos, ntt, cos_tt)
        nttm[npos] = nttm[npos].union(cos_tt)
    for npos, tts in nttm.items():
        print(npos, tts)
        curr_tt = curr_tt.intersection(tts)
    print(curr_tt)
    return curr_tt


def update_map(
    cmap: dict[Position, set[TileType]],
    nmap: dict[Position, Optional[Tile]],
    cm: ConstraintMap,
    nm: neighbors_map,
) -> dict[Position, set[TileType]]:
    new_cmap: dict[Position, set[TileType]] = dict()
    for pos in cmap.keys():
        if nmap[pos] is not None:
            new_cmap[pos] = cmap[pos]
            continue
        new_cmap[pos] = propagate_neighbors(cmap, pos, cm, nm)
    return new_cmap


def gen_coord_space(xsize: int, ysize: int) -> list[Position]:
    vects = []
    lnx = np.linspace(0, xsize - 1, xsize)
    lny = np.linspace(0, ysize - 1, ysize)
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    def toVect2(x) -> Position:
        return Position(x[0], x[1])

    for coord in coords:
        vects.append(toVect2(coord))
    return vects


def init_collapsable(xsize: int, ysize: int) -> WFCCollapsble:
    tg: WFCCollapsble = Collapsable(constraints={}, nodes={})
    coords = gen_coord_space(xsize, ysize)
    for coord in coords:
        tg.nodes[coord] = None
        tg.constraints[coord] = TL
        print(tg.constraints[coord])
    return tg


def main():
    test_tg = init_collapsable(3, 3)
    wave_function_collapse(test_tg, lambda x: False, generate_constraint_map(ucm))
    test_tg.print_nodes()


if __name__ == "__main__":
    print(generate_constraint_map(ucm))
    main()


#####
#
#
#    ->
#
