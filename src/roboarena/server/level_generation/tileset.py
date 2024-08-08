from bidict import bidict

from roboarena.server.level_generation.level_generator import Tile, Tileset
from roboarena.shared.block import floor, void, wall

w = wall
f = floor
v = void

cr = cross = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, f, f, f, w),
    ),
)
lv = line_vertical = Tile(
    (
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
        (w, f, f, f, w),
    ),
)
lh = line_horizontal = Tile(
    (
        (w, w, w, w, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, w, w, w, w),
    ),
)
tn = t_normal = Tile(
    (
        (w, w, w, w, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, f, f, f, w),
    ),
)
ti = t_inverse = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (f, f, f, f, f),
        (w, w, w, w, w),
    ),
)
en = e_normal = Tile(
    (
        (w, f, f, f, w),
        (w, f, f, f, f),
        (w, f, f, f, f),
        (w, f, f, f, f),
        (w, f, f, f, w),
    ),
)
ei = e_inverse = Tile(
    (
        (w, f, f, f, w),
        (f, f, f, f, w),
        (f, f, f, f, w),
        (f, f, f, f, w),
        (w, f, f, f, w),
    ),
)
wa = walls = Tile(
    (
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
        (w, w, w, w, w),
    )
)
fallback = Tile(
    (
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
        (v, v, v, v, v),
    )
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
tileset = Tileset.from_example(example, dict(str_tile_dict), fallback)
