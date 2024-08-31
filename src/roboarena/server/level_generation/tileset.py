from bidict import bidict

from roboarena.server.level_generation.level_generator import (
    Edge,
    Tile,
    Tileset,
    rotations,
)
from roboarena.shared.block import (
    floor,
    floor_door,
    floor_room,
    floor_room_spawn,
    void,
    wall,
)
from roboarena.shared.util import dedupe

" Blocks "

w = wall
f = floor
r = floor_room
X = floor_room_spawn
d = floor_door
v = void

blocks = bidict({"#": wall, ".": floor, "X": floor_room_spawn, "+": floor_door, " ": v})


" Edges "

e_floor = Edge()
e_void = Edge()


" Tiles "

end = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, w, w, w, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_void, e_floor, e_void),
)
end_room = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, X, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_void, e_floor, e_void),
)
line = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_floor, e_void, e_floor, e_void),
)
line_room = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, X, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_floor, e_void, e_floor, e_void),
)
corner = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, w, w, w, w, w, w, w, w, w, w),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_floor, e_floor, e_void),
)
corner_room = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (v, v, v, v, v, w, r, r, r, r, r, r, X, r, r, r, r, r, r, d, f, f, f, f, f),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_floor, e_floor, e_void),
)
tee = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (w, w, w, w, w, w, w, w, w, w, w, f, f, f, w, w, w, w, w, w, w, w, w, w, w),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_floor, e_floor, e_floor),
)
tee_room = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (w, w, w, w, w, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (f, f, f, f, f, d, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (f, f, f, f, f, d, r, r, r, r, r, r, X, r, r, r, r, r, r, d, f, f, f, f, f),
        (f, f, f, f, f, d, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (w, w, w, w, w, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_void, e_floor, e_floor, e_floor),
)
cross = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (w, w, w, w, w, w, w, w, w, w, w, f, f, f, w, w, w, w, w, w, w, w, w, w, w),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f),
        (w, w, w, w, w, w, w, w, w, w, w, f, f, f, w, w, w, w, w, w, w, w, w, w, w),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_floor, e_floor, e_floor, e_floor),
)
cross_room = Tile(
    (
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (w, w, w, w, w, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (f, f, f, f, f, d, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (f, f, f, f, f, d, r, r, r, r, r, r, X, r, r, r, r, r, r, d, f, f, f, f, f),
        (f, f, f, f, f, d, r, r, r, r, r, r, r, r, r, r, r, r, r, d, f, f, f, f, f),
        (w, w, w, w, w, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, w, w, w, w, w),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, r, r, r, r, r, r, r, r, r, r, r, r, r, w, v, v, v, v, v),
        (v, v, v, v, v, w, w, w, w, w, w, d, d, d, w, w, w, w, w, w, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
        (v, v, v, v, v, v, v, v, v, v, w, f, f, f, w, v, v, v, v, v, v, v, v, v, v),
    ),
    edges=(e_floor, e_floor, e_floor, e_floor),
)
fallback = Tile(
    (
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
        (w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w),
    ),
    edges=(Edge(), Edge(), Edge(), Edge()),
)

tiles = bidict(
    (
        *zip("╵╶╷╴", rotations(end)),
        *zip("╹╺╻╸", rotations(end_room)),
        *zip("│─", dedupe(rotations(line))),
        *zip("┃━", dedupe(rotations(line_room))),
        *zip("┌┐┘└", rotations(corner)),
        *zip("┏┓┛┗", rotations(corner_room)),
        *zip("┬┤┴├", rotations(tee)),
        *zip("┳┫┻┣", rotations(tee_room)),
        *zip("┼", [cross]),
        *zip("╋", [cross_room]),
        ("█", fallback),
        # (" ", None),
    )
)


" Tileset "

# example = """
# ███├─┴─┬─┤██
# ███│███│█│██
# ─┬─┤███├─┴─┬
# █│█│███│███│
# █├─┴─┬─┤███├
# █│███│█│███│
# ─┤███├─┴─┬─┤
# █│███│███│█│
# ─┴─┬─┤███├─┴
# ███│█│███│██
# ███├─┴─┬─┤██
# """
# tileset = Tileset.from_example(example, dict(tiles), fallback, tee)
tileset = Tileset.from_edges(tiles.values(), fallback, cross)
