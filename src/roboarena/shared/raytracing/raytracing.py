# import math
# from collections import defaultdict
# from typing import TYPE_CHECKING, Callable
#
# from roboarena.server.level_generation.tileset import end_room, floor, floor_room
# from roboarena.shared.block import Block
# from roboarena.shared.raytracing.tuple_util import Line
# from roboarena.shared.utils.timer import Timer
# from roboarena.shared.utils.tuple_rect import Rect
# from roboarena.shared.utils.vector import Vector
#
# if TYPE_CHECKING:
#     from roboarena.shared.rendering.renderer import FieldOfView
# type Level = dict[Vector[int], "Block"]
# type LightLevel = dict[Vector[int], float]
#
# type RenderDebugRay = Callable[[Vector[float], Vector[float]], None]
# type RenderDebugIntersection = Callable[[Vector[float]], None]
#
#
# type BlockChunk = list[tuple[Vector[int], Block]]
#
#
# class Grid:
#     grid: dict[tuple[int, int], BlockChunk]
#
#     def __init__(self, level: Level, cell_size: int = 2):
#         self.cell_size = cell_size
#         self.grid = defaultdict(list)
#         for pos, block in level.items():
#             cell = (pos.x // cell_size, pos.y // cell_size)
#             self.grid[cell].append((pos, block))
#
#     def get_blocks_in_range(
#         self, start: Vector[float], end: Vector[float]
#     ) -> BlockChunk:
#         start_cell = (int(start.x) // self.cell_size, int(start.y) // self.cell_size)
#         end_cell = (int(end.x) // self.cell_size, int(end.y) // self.cell_size)
#
#         blocks: BlockChunk = []
#         for x in range(
#             min(start_cell[0], end_cell[0]), max(start_cell[0], end_cell[0]) + 1
#         ):
#             for y in range(
#                 min(start_cell[1], end_cell[1]), max(start_cell[1], end_cell[1]) + 1
#             ):
#                 if (x, y) in self.grid:
#                     blocks.extend(self.grid[(x, y)])
#         return blocks
#
#
# def calculate_light(
#     level: Level,
#     ppos: Vector[float],
#     fov: "FieldOfView",
#     rdr: RenderDebugRay,
#     rdi: RenderDebugIntersection,
#     _timer: Timer,
# ) -> LightLevel:
#     _timer.tick("total")
#     # Returns all blocks that are illuminated by the light source and their light level
#
#     light_levels: dict[Vector[int], float] = {}
#     light_source = ppos
#     # = next(
#     #     (pos for pos, block in level.items() if block.is_light_source), None
#     # )
#
#     if not light_source:
#         return light_levels
#
#     max_distance = fov.half_diag
#     num_rays = 100  # Number of rays to cast
#     max_bounces = 5  # Maximum number of reflections
#     level_grid = Grid(level)
#     tfov = Rect.from_vect_rect(fov)
#
#     count = 0
#
#     def cast_ray(
#         origin: Vector[float],
#         direction: Vector[float],
#         energy: float,
#         bounces: int,
#         rdr,
#         rdi,
#     ) -> int:
#         count = 0
#         if bounces > max_bounces or energy < 0.05:
#             return 0
#
#         ray = Line(origin, direction, restrict=(0, float("inf")))
#         _timer.tick("get_blocks_to_check")
#         blocks_to_check = level_grid.get_blocks_in_range(
#             origin, origin + direction * max_distance
#         )
#         _timer.tick_end()
#         nearest_intersection = None
#         nearest_distance = float("inf")
#         _timer.tick("find_intersections")
#         for pos, block in blocks_to_check:
#             tfov_check = tfov.contains(pos.to_tuple())
#             if (
#                 block.render_above_entities and tfov_check
#             ):  # TODO check if this is correct
#                 for edge in block.edges_at(pos):
#                     intersection = edge.intersection(ray)
#                     # edge.render(rdr)
#                     count += 1
#                     if intersection:
#                         distance = (intersection - origin).length()
#                         if distance < nearest_distance:
#                             nearest_distance = distance
#                             nearest_intersection = (intersection, pos, block)
#         _timer.tick_end()
#         _timer.tick("reflections")
#         _timer.tick_end()
#         if nearest_intersection:
#             _timer.tick("update_light")
#             intersection, block_pos, block = nearest_intersection
#             rdr(origin, intersection, (0, 200, 0))
#
#             # Update light level for the intersected block
#             current_pos = origin
#             step = direction.normalize() * 0.5  # Small step size
#             while (current_pos - origin).length() <= nearest_distance:
#                 block_pos = current_pos.to_int()
#                 if block_pos in level:
#                     distance = (current_pos - origin).length()
#                     light_level = energy * (1 - distance / nearest_distance)
#                     light_levels[block_pos] = max(
#                         light_levels.get(block_pos, 0), light_level
#                     )
#                 current_pos += step
#             _timer.tick_end()
#             # _timer.tick("reflections")
#             # Handle reflection
#             if block.reflectivity > 0:
#                 normal = block.get_normal(block_pos, intersection)
#                 reflected_direction = direction - normal * 2 * Vector.dot(
#                     direction, normal
#                 )
#                 reflected_energy = energy * block.reflectivity
#                 cast_ray(
#                     intersection + reflected_direction * 0.01,
#                     reflected_direction,
#                     reflected_energy,
#                     bounces + 1,
#                     rdr,
#                     rdi,
#                 )
#             # _timer.tick_end()
#         return count
#
#     # Cast rays in random directions
#     a_step = 2 * math.pi / num_rays
#     c = 0
#     for i in range(num_rays):
#
#         angle = a_step * i
#         direction = Vector.from_angle(angle)
#         r = Line(ppos, direction, restrict=(0, 10))
#
#         def col(i):
#             c = int(255 * ((i) / num_rays))
#             return c
#
#         def rdra(s, e, c=None):
#             if c is None:
#                 rdr(s, e, (255, col(i), 0))
#             else:
#
#                 rdr(s, e, c)
#
#         def rdia(s, c=None):
#             rdi(s, (255, col(i), 0))
#
#         r.render(rdra)
#         c += cast_ray(light_source, direction, 1, 0, rdra, rdia)
#     # Normalize light levels
#     max_light = max(light_levels.values(), default=1)
#     for pos in light_levels:
#         light_levels[pos] /= max_light
#     _timer.tick_end()
#     _timer.end_run()
#     return light_levels
import math
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, NamedTuple, Optional

from roboarena.shared.block import Block
from roboarena.shared.raytracing.tuple_util import Line
from roboarena.shared.utils.timer import Timer
from roboarena.shared.utils.tuple_rect import Rect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import FieldOfView

FloatVector = tuple[float, float]
IntVector = tuple[int, int]
LightLevel = dict[IntVector, float]
BlockChunk = list[tuple[IntVector, Block]]

RenderDebugRay = Callable[[FloatVector, FloatVector], None]
RenderDebugIntersection = Callable[[FloatVector], None]


class Grid:
    def __init__(self, level: dict[Vector[int], Block], cell_size: int = 2):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        for pos, block in level.items():
            cell = (pos.x // cell_size, pos.y // cell_size)
            self.grid[cell].append(((pos.x, pos.y), block))

    def get_blocks_in_range(self, start: FloatVector, end: FloatVector) -> BlockChunk:
        start_cell = (int(start[0]) // self.cell_size, int(start[1]) // self.cell_size)
        end_cell = (int(end[0]) // self.cell_size, int(end[1]) // self.cell_size)

        blocks: BlockChunk = []
        for x in range(
            min(start_cell[0], end_cell[0]), max(start_cell[0], end_cell[0]) + 1
        ):
            for y in range(
                min(start_cell[1], end_cell[1]), max(start_cell[1], end_cell[1]) + 1
            ):
                blocks.extend(self.grid.get((x, y), []))
        return blocks


class RayContext(NamedTuple):
    level_grid: Grid
    max_distance: float
    max_bounces: int
    tfov: Rect
    light_levels: LightLevel
    rdr: RenderDebugRay
    rdi: RenderDebugIntersection
    timer: Timer


def distance(a: FloatVector, b: FloatVector) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def normalize(v: FloatVector) -> FloatVector:
    length = math.hypot(v[0], v[1])
    return (v[0] / length, v[1] / length)


def dot_product(a: FloatVector, b: FloatVector) -> float:
    return a[0] * b[0] + a[1] * b[1]


def reflect(d: FloatVector, n: FloatVector) -> FloatVector:
    dot = dot_product(d, n)
    return (d[0] - 2 * dot * n[0], d[1] - 2 * dot * n[1])


def find_nearest_intersection(
    ray: Line, blocks: BlockChunk, ctx: RayContext
) -> tuple[Optional[FloatVector], Optional[IntVector], Optional[Block]]:
    ctx.timer.tick("find_intersections")
    nearest_intersection = None
    nearest_distance = float("inf")
    nearest_block_pos = None
    nearest_block = None

    for pos, block in blocks:
        if block.render_above_entities and ctx.tfov.contains(pos):
            for edge in block.edges_at(Vector(*pos)):
                intersection = edge.intersection(ray)
                if intersection:
                    dist = distance(ray.origin, intersection)
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_intersection = intersection
                        nearest_block_pos = pos
                        nearest_block = block

    ctx.timer.tick_end()
    return nearest_intersection, nearest_block_pos, nearest_block


def update_light_levels(
    origin: FloatVector,
    end: FloatVector,
    energy: float,
    blocks: BlockChunk,
    ctx: RayContext,
) -> None:
    ctx.timer.tick("update_light")
    direction = normalize((end[0] - origin[0], end[1] - origin[1]))
    step_length = 0.5
    step = (direction[0] * step_length, direction[1] * step_length)
    current_pos = origin
    max_distance = distance(origin, end)

    while distance(current_pos, origin) <= max_distance:
        block_pos = (int(current_pos[0]), int(current_pos[1]))
        if block_pos in dict(blocks):
            dist = distance(current_pos, origin)
            light_level = energy * (1 - dist / max_distance)
            ctx.light_levels[block_pos] = max(
                ctx.light_levels.get(block_pos, 0), light_level
            )
        current_pos = (current_pos[0] + step[0], current_pos[1] + step[1])

    ctx.timer.tick_end()


def cast_ray(
    origin: FloatVector,
    direction: FloatVector,
    energy: float,
    bounces: int,
    ctx: RayContext,
) -> int:
    if bounces > ctx.max_bounces or energy < 0.05:
        return 0

    ray = Line(origin, direction, restrict=(0, ctx.max_distance))
    ctx.timer.tick("get_blocks_to_check")
    end_point = (
        origin[0] + direction[0] * ctx.max_distance,
        origin[1] + direction[1] * ctx.max_distance,
    )
    blocks_to_check = ctx.level_grid.get_blocks_in_range(origin, end_point)
    ctx.timer.tick_end()

    nearest_intersection, block_pos, block = find_nearest_intersection(
        ray, blocks_to_check, ctx
    )

    if nearest_intersection:
        ctx.rdr(origin, nearest_intersection, (0, 200, 0))
        update_light_levels(origin, nearest_intersection, energy, blocks_to_check, ctx)

        if block and block.reflectivity > 0:
            normal_tuple = block.get_normal(
                Vector(*block_pos), Vector(*nearest_intersection)
            )
            reflected_direction = reflect(direction, normal_tuple)
            reflected_energy = energy * block.reflectivity
            reflected_origin = (
                nearest_intersection[0] + reflected_direction[0] * 0.01,
                nearest_intersection[1] + reflected_direction[1] * 0.01,
            )
            return 1 + cast_ray(
                reflected_origin,
                reflected_direction,
                reflected_energy,
                bounces + 1,
                ctx,
            )

    return 1


def calculate_light(
    level: dict[Vector[int], Block],
    ppos: Vector[float],
    fov: "FieldOfView",
    rdr: RenderDebugRay,
    rdi: RenderDebugIntersection,
    timer: Timer,
) -> LightLevel:
    timer.tick("total")

    light_levels: LightLevel = {}
    light_source = (ppos.x, ppos.y)

    if not light_source:
        return light_levels

    num_rays = 10  # Number of rays to cast
    max_bounces = 5  # Maximum number of reflections
    level_grid = Grid(level)
    tfov = Rect.from_vect_rect(fov)
    max_distance = tfov.half_diag

    ctx = RayContext(
        level_grid, max_distance, max_bounces, tfov, light_levels, rdr, rdi, timer
    )

    # Pre-compute ray directions
    ray_directions = [
        (math.cos(a), math.sin(a))
        for a in [2 * math.pi * i / num_rays for i in range(num_rays)]
    ]

    for direction in ray_directions:
        cast_ray(light_source, direction, 1, 0, ctx)

    # Normalize light levels
    max_light = max(light_levels.values(), default=1)
    for pos in light_levels:
        light_levels[pos] /= max_light

    timer.tick_end()
    timer.end_run()
    return light_levels
