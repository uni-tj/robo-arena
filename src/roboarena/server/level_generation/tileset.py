from bidict import bidict

from roboarena.server.level_generation.level_generator import Edge, Tile, Tileset
from roboarena.shared.block import floor, void, wall

w = wall
f = floor
v = void

e_floor = Edge()
e_wall = Edge()

cr = cross = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, f, f, f, w),
    ),
    edges=(e_floor, e_floor, e_floor, e_floor),
)
lv = line_vertical = Tile(
    (
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
    ),
    edges=(e_floor, e_wall, e_floor, e_wall),
)
lh = line_horizontal = Tile(
    (
        (w, w, w, w, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, w, w, w, w),
    ),
    edges=(e_wall, e_floor, e_wall, e_floor),
)
tn = t_normal = Tile(
    (
        (w, w, w, w, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, f, f, f, w),
    ),
    edges=(e_wall, e_floor, e_floor, e_floor),
)
ti = t_inverse = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, w, w, w, w),
    ),
    edges=(e_floor, e_floor, e_wall, e_floor),
)
en = e_normal = Tile(
    (
        (w, f, f, f, w),
        (w, f, f, f, f),
        (w, f, f, f, f),
        (w, f, f, f, f),
        (w, f, f, f, w),
    ),
    edges=(e_floor, e_floor, e_floor, e_wall),
)
ei = e_inverse = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, w),
        (f, f, f, f, w),
        (f, f, f, f, w),
        (w, f, f, f, w),
    ),
    edges=(e_floor, e_wall, e_floor, e_floor),
)
wa = walls = Tile(
    (
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
    ),
    edges=(e_wall, e_wall, e_wall, e_wall),
)
fallback = Tile(
    (
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
    ),
    edges=(Edge(), Edge(), Edge(), Edge()),
)

# mapping for debugging. Not used by production code.
str_tile_dict = bidict(
    {
        # "┼": cross,
        "│": line_vertical,
        "─": line_horizontal,
        "┬": t_normal,
        "┴": t_inverse,
        "├": e_normal,
        "┤": e_inverse,
        "█": walls,
        # "╳": fallback,
        " ": None,
    }
)

example = """
███├─┴─┬─┤██
███│███│█│██
─┬─┤███├─┴─┬
█│█│███│███│
█├─┴─┬─┤███├
█│███│█│███│
─┤███├─┴─┬─┤
█│███│███│█│
─┴─┬─┤███├─┴
███│█│███│██
███├─┴─┬─┤██
"""
# tileset = Tileset.from_example(example, dict(str_tile_dict), fallback)
tileset = Tileset.from_edges([cr, lv, lh, tn, ti, en, ei, wa], fallback)
