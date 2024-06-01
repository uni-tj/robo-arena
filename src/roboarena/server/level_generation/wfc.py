import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from roboarena.server.level_generation.tile import Tile, TileType
from roboarena.shared.util import gen_coord_space, getBounds
from roboarena.shared.utils.vector import Vector


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


@dataclass
class WfcCtx:
    constraints: dict[Vector[int], set[TileType]]
    nodes: dict[Vector[int], Optional[Tile]]

    def print_constraints(self):
        print_constraint_grid(self.constraints)

    def print_nodes(self):
        print_grid(self.nodes)

    def add_nodes(self, pos_list: list[Vector[int]], tl: set[TileType]) -> None:
        for pos in pos_list:
            self.constraints[pos] = tl
            self.nodes[pos] = None


# Switching from the user specified Constraint map to a less error prone variant that
# is not directional
class Direction(Enum):
    UP = Vector[int](0, -1)
    DOWN = Vector[int](0, 1)
    LEFT = Vector[int](-1, 0)
    RIGHT = Vector[int](1, 0)


@dataclass(frozen=True)
class UserConstraint:
    direction: list[Direction]
    tt: TileType
    tiles: list[TileType]


UserConstraintList = list[UserConstraint]
Constraint = dict[Vector[int], set[TileType]]
ConstraintMap = dict[TileType, Constraint]

TL = set(x for x in TileType.__members__.values())


def get_grid(nodes: dict[Vector[int], Optional["Tile"]]):
    """Returns a grid-like representation of the nodes,
    arranged by their (x, y) positions."""

    (v_min, v_max) = getBounds(list(nodes.keys()))
    (min_x, min_y) = v_min.tuple_repr()
    (max_x, max_y) = v_max.tuple_repr()
    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for position, cons in nodes.items():
        x, y = position.tuple_repr()
        grid[y - min_y][x - min_x] = str(cons) if cons is not None else "⑔"
    return grid


def get_constraint_grid(constraints: dict[Vector[int], set["TileType"]]):
    position = constraints
    max_x = max(position, key=lambda x: x.x).x
    min_x = min(position, key=lambda x: x.x).x
    max_y = max(position, key=lambda x: x.y).y
    min_y = min(position, key=lambda x: x.y).y
    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for position, cons in constraints.items():
        x, y = position.tuple_repr()
        ns = "".join(map(lambda x: x.name, cons))
        grid[y - min_y][x - min_x] = ns
    return grid


def print_grid(nodes: dict[Vector[int], Optional["Tile"]]):
    print("\n".join(map(lambda x: "".join(x), get_grid(nodes))))


def print_constraint_grid(constraints: dict[Vector[int], set["TileType"]]):
    grid = map(
        lambda x: x + "\n" + "-" * len(x),
        map(
            lambda x: "|".join(map(lambda x: str(x).ljust(10), x)),
            get_constraint_grid(constraints),
        ),
    )
    print("\n".join(grid))


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


def generate_constraint_map(ucm: UserConstraintList) -> ConstraintMap:
    # This function converts a UserConstraintList into a ConstraintMap that is usable
    # for internal ease of use
    cm: ConstraintMap = {}
    for const in ucm:
        match const:
            case UserConstraint(dirs, tt, tiles):
                for dir in dirs:
                    # Update all  outgoing tiles
                    if tt not in cm:
                        cm[tt] = {}
                    if dir.value not in cm[tt]:
                        cm[tt][dir.value] = set()

                    cm[tt][dir.value] = cm[tt][dir.value].union(set(tiles))

                    # Update all incoming tiles
                    for ntt in tiles:
                        if ntt not in cm:
                            cm[ntt] = {}
                        idir = (dir.value * Vector[int](-1, -1)).round()
                        if idir.floor() not in cm[ntt]:
                            cm[ntt][idir] = set()
                        cm[ntt][idir] = cm[ntt][idir].union(set([tt]))
    return cm


def get_collapsable(tg: WfcCtx) -> Optional[Vector[int]]:
    collapseable: dict[int, list[Vector[int]]] = {}
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
    return Tile(tt.value, tt, {})


def wave_function_collapse(
    tg: WfcCtx,
    consttraint_map: ConstraintMap,
):
    selected_tile = get_collapsable(tg)
    while selected_tile is not None:
        pos_tiles: set[TileType] = tg.constraints[selected_tile]
        selected_type = random.choice(list(pos_tiles))
        propagate(tg, selected_tile, selected_type, consttraint_map)
        selected_tile = get_collapsable(tg)


def propagate(
    tg: WfcCtx, pos: Vector[int], tt: TileType, constraints: ConstraintMap
) -> None:
    # ! Mutates the tg WfcCtx in place
    tg.constraints[pos] = set([tt])
    tg.nodes[pos] = construct_Tile(tt)
    old_map = tg.constraints
    new_map = {}
    # Propagate Information until the map doesn't change
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


neighbors_map = list[tuple[TileType, Vector[int]]]


def calculate_neighbors(
    map: dict[Vector[int], set[TileType]], pos: Vector[int], cm: neighbors_map
) -> list[tuple[TileType, Vector[int], Vector[int]]]:
    # calculate the possible Neighbortiles
    nl: list[tuple[TileType, Vector[int], Vector[int]]] = []
    for ntt, dir in cm:
        npos = (pos - dir).round()
        if npos not in map or ntt not in map[npos]:
            continue
        nl.append((ntt, npos, dir))
    return nl


def generate_neighbors_map(cm: ConstraintMap) -> neighbors_map:
    res: neighbors_map = []
    for ntt, consts in cm.items():
        for dir, _ in consts.items():
            res.append((ntt, dir))
    return res


def propagate_neighbors(
    cmap: dict[Vector[int], set[TileType]],
    pos: Vector[int],
    cm: ConstraintMap,
    nm: neighbors_map,
) -> set[TileType]:
    # Update the Tile at position pos to be constrained by the neighboring tiles
    curr_tt = TL
    nl: list[tuple[TileType, Vector[int], Vector[int]]] = calculate_neighbors(
        cmap, pos, nm
    )
    nttm: dict[Vector[int], set[TileType]] = {}

    # Update the implied constraints resulting from possible neighbor tiles
    for ntt, npos, ndir in nl:
        if ntt not in cmap[npos]:
            continue
        if npos not in nttm:
            nttm[npos] = set()

        cos_tt = cm[ntt][ndir]
        nttm[npos] = nttm[npos].union(cos_tt)

    # Unify the Constraints from all neigbors
    for _, tts in nttm.items():
        curr_tt = curr_tt.intersection(tts)
    return curr_tt


def update_map(
    cmap: dict[Vector[int], set[TileType]],
    nmap: dict[Vector[int], Optional[Tile]],
    cm: ConstraintMap,
    nm: neighbors_map,
) -> dict[Vector[int], set[TileType]]:
    new_cmap: dict[Vector[int], set[TileType]] = dict()
    for pos in cmap.keys():
        if nmap[pos] is not None:
            new_cmap[pos] = cmap[pos]
            continue
        new_cmap[pos] = propagate_neighbors(cmap, pos, cm, nm)
    return new_cmap


def init_collapsable(xsize: int, ysize: int) -> WfcCtx:
    tg: WfcCtx = WfcCtx(constraints={}, nodes={})
    coords = gen_coord_space(xsize, ysize)
    for coord in coords:
        tg.nodes[coord] = None
        tg.constraints[coord] = TL
    return tg


def main():
    test_tg = init_collapsable(3, 3)
    wave_function_collapse(test_tg, generate_constraint_map(ucm))
    test_tg.print_nodes()


if __name__ == "__main__":
    print(generate_constraint_map(ucm))
    main()
