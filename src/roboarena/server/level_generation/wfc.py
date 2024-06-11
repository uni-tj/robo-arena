import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Optional

from funcy import log_durations

# from roboarena.server.level_generation.level_config import UCM
from roboarena.server.level_generation.tile import BasicTile, Tile, TileType
from roboarena.shared.types import ConstraintMap, UserConstraint, UserConstraintList
from roboarena.shared.util import gen_coord_space, getBounds
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


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


TL = set(x for x in TileType.__members__.values())


def print_constraints_as_json(constraints: ConstraintMap):
    constraints_dict = {
        str(tile_types): [
            [str(dir), list(map(lambda x: x.value, cons))]
            for dir, cons in inner.items()
        ]
        for tile_types, inner in constraints.items()
    }
    print(json.dumps(constraints_dict, indent=2, ensure_ascii=False))


@dataclass
class WfcCtx:
    constraints: dict[Vector[int], set[TileType]]
    nodes: dict[Vector[int], Optional["BasicTile"]]
    open_tiles: "ChangedTiles"

    @log_durations(logger.critical, "init_square: ", "ms")
    def init_square(self, xsize: int, ysize: int):
        coords = gen_coord_space((0, xsize), (0, ysize))
        for coord in coords:
            self.nodes[coord] = None
            self.constraints[coord] = TL
            self.open_tiles.add(coord)

    def print_constraints(self):
        print_constraint_grid(self.constraints)

    def print_nodes(self):
        print_grid(self.nodes)

    def add_nodes(self, pos_list: list[Vector[int]], tl: set[TileType]) -> bool:
        update = False
        added_nodes: set[Vector[int]] = set()
        for pos in pos_list:
            if pos in self.nodes:
                continue
            update = True
            added_nodes.add(pos)
            self.constraints[pos] = tl
            self.nodes[pos] = None
            self.open_tiles.add(pos)
        if update:
            print(added_nodes)
        return update


# Switching from the user specified Constraint map to a less error prone variant that
# is not directional


def get_grid(nodes: dict[Vector[int], Optional["Tile"]]):
    """Returns a grid-like representation of the nodes,
    arranged by their (x, y) positions."""

    (v_min, v_max) = getBounds(list(nodes.keys()))
    (min_x, min_y) = v_min.to_tuple()
    (max_x, max_y) = v_max.to_tuple()
    grid = [[" " for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for position, cons in nodes.items():
        x, y = position.to_tuple()
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
        x, y = position.to_tuple()
        ns = "".join(map(lambda x: x.name, cons))
        grid[y - min_y][x - min_x] = ns
    return grid


def print_grid(nodes: dict[Vector[int], Optional["BasicTile"]]):
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


def generate_constraint_map(ucm: UserConstraintList) -> ConstraintMap:
    # This function converts a UserConstraintList into a ConstraintMap that is usable
    # for internal ease of use
    cm: ConstraintMap = {}
    for const in ucm:
        match const:
            case UserConstraint(tt, constrs):
                for dir, tiles in constrs.items():
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


# @log_durations(logger.critical, "getCollapsable: ", "ms")
def get_collapsable(tg: WfcCtx) -> Optional[Vector[int]]:
    collapseable: dict[int, list[Vector[int]]] = {}
    min_constr = len(TL) + 1

    for pos, node in tg.nodes.items():
        if node is not None:
            continue

        num_constraints = len(tg.constraints[pos])
        if num_constraints == 0:
            continue
        if num_constraints < min_constr:
            min_constr = num_constraints
            collapseable = {min_constr: [pos]}
        elif num_constraints == min_constr:
            collapseable[min_constr].append(pos)

    if len(collapseable) == 0:
        return None

    return random.choice(collapseable[min_constr])


def construct_Tile(tt: TileType) -> BasicTile:
    return BasicTile(tt)


# @log_durations(logger.critical, "wfc: ", "ms")
def wave_function_collapse(
    tg: WfcCtx,
    consttraint_map: ConstraintMap,
):
    selected_tile = get_collapsable(tg)

    num_iter = 0
    pat = 0
    cat = 0
    end_pred = all(map(lambda x: x is not None, tg.nodes.values()))
    while selected_tile is not None and not end_pred:
        num_iter += 1
        pos_tiles: set[TileType] = tg.constraints[selected_tile]
        selected_type = random.choice(list(pos_tiles))
        t0 = time.time()
        propagate(tg, selected_tile, selected_type, consttraint_map)
        pat += time.time() - t0
        t1 = time.time()
        selected_tile = get_collapsable(tg)
        cat += time.time() - t1
    print(
        f"{bcolors.WARNING}pat: {pat*1000}, cat: {cat*1000},  Num Iterations: {num_iter} {bcolors.ENDC}"
    )


# @log_durations(logger.critical, "propagate: ", "ms")
def propagate(
    tg: WfcCtx, pos: Vector[int], tt: TileType, constraints: ConstraintMap
) -> None:
    # ! Mutates the tg WfcCtx in place
    tg.constraints[pos] = set([tt])
    tg.nodes[pos] = construct_Tile(tt)
    old_map = tg.constraints
    new_map = {}
    tg.open_tiles.remove(pos)
    # Propagate Information until the map doesn't change
    while new_map != old_map and len(tg.open_tiles) > 0:  # and not len(cnt) == 0:
        res, _ = update_map(
            old_map,
            tg.nodes,
            constraints,
            generate_neighbors_map(constraints),
            tg.open_tiles,
        )
        if new_map != {}:
            old_map = new_map

        new_map = res
    # print(bcolors.FAIL + "Finsihed iteration" + bcolors.ENDC)
    tg.constraints = new_map
    # tg.print_constraints()


neighbors_map = list[tuple[TileType, Vector[int]]]


# @log_durations(logger.critical, "calculate_neighbors: ", "ms")
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


# @log_durations(logger.critical, "generate_neighbors_map: ", "ms")
def generate_neighbors_map(cm: ConstraintMap) -> neighbors_map:
    res: neighbors_map = []
    for ntt, consts in cm.items():
        for dir, _ in consts.items():
            res.append((ntt, dir))
    return res


type ChangedTiles = set[Vector[int]]


# @log_durations(logger.critical, "propagate_neighbors: ", "ms")
def propagate_neighbors(
    cmap: dict[Vector[int], set[TileType]],
    pos: Vector[int],
    cm: ConstraintMap,
    nm: neighbors_map,
) -> tuple[set[TileType], ChangedTiles]:
    # Update the Tile at position pos to be constrained by the neighboring tiles
    curr_tt = TL
    nl: list[tuple[TileType, Vector[int], Vector[int]]] = calculate_neighbors(
        cmap, pos, nm
    )
    nttm: dict[Vector[int], set[TileType]] = {}

    # Update the implied constraints resulting from possible neighbor tiles
    # restrictors: dict[str, list[tuple[str, list[str]]]] = {}
    for ntt, npos, ndir in nl:
        # if str(npos) not in restrictors:
        #     restrictors[str(npos)] = []
        if ntt not in cmap[npos]:
            continue
        if npos not in nttm:
            nttm[npos] = set()

        cos_tt = cm[ntt][ndir]
        # restrictors[str(npos)].append((str(ntt), list(map(lambda x: str(x), cos_tt))))
        nttm[npos] = nttm[npos].union(cos_tt)
    # Unify the Constraints from all neigbors
    changed_neighbors: set[Vector[int]] = set(nttm.keys())
    # logger.critical(f" changed_neig{changed_neighbors}")
    # for npos, tts in nttm.items():
    #     curr_tt = curr_tt.intersection(tts)
    #     changed_neighbors.add(npos)
    curr_tt.intersection(*nttm.values())
    # changed_neighbors = set(nttm.keys())
    # if curr_tt == set():
    # print(json.dumps(restrictors, indent=2))
    # print_constraints_as_json(cm)
    return curr_tt, changed_neighbors


# @log_durations(logger.critical, "update_map: ", "ms")
def update_map(
    cmap: dict[Vector[int], set[TileType]],
    nmap: dict[Vector[int], Optional[BasicTile]],
    cm: ConstraintMap,
    nm: neighbors_map,
    ct: ChangedTiles,
) -> tuple[dict[Vector[int], set[TileType]], ChangedTiles]:
    new_cmap: dict[Vector[int], set[TileType]] = dict()
    apt = 0
    # print_constraint_grid(cmap)
    # print_grid(nmap)
    i = 0
    cnt: ChangedTiles = set()
    for pos in ct:
        # print(pos)
        if nmap[pos] is not None:
            new_cmap[pos] = cmap[pos]
            _, ctt = propagate_neighbors(cmap, pos, cm, nm)
            cnt = cnt.union(ctt)
            # logger.critical(f" Nmap[pos]: {nmap[pos]}")
            continue
        t0 = time.time()
        i += 1
        new_cmap[pos], cct = propagate_neighbors(cmap, pos, cm, nm)
        cnt = cnt.union(cct)

        # print(f"cnt {cnt} cnt")
        apt += time.time() - t0
    # print(cnt)
    logger.critical(f"apt,i  {apt} {i}")
    # input()
    return new_cmap, cnt


def init_collapsable(xsize: int, ysize: int) -> WfcCtx:
    tg: WfcCtx = WfcCtx(constraints={}, nodes={})
    coords = gen_coord_space((0, xsize), (0, ysize))
    for coord in coords:
        tg.nodes[coord] = None
        tg.constraints[coord] = TL
    return tg


# def main():
#     ucm = UCM
#     test_tg = init_collapsable(10, 10)
#     # print_constraints_as_json(generate_constraint_map(ucm))
#     wave_function_collapse(test_tg, generate_constraint_map(ucm))
#     # test_tg.print_nodes()


# if __name__ == "__main__":

#     main()
