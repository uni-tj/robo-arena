import math
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, NamedTuple, Optional

from roboarena.shared.block import Block
from roboarena.shared.raytracing.tuple_util import Line
from roboarena.shared.types import Level
from roboarena.shared.utils.timer import Timer
from roboarena.shared.utils.tuple_rect import Rect
from roboarena.shared.utils.tuple_vector import add_tuples
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import FieldOfView

FloatVector = tuple[float, float]
IntVector = tuple[int, int]
LightLevel = dict[IntVector, float]
BlockChunk = list[tuple[IntVector, Block]]

RenderDebugRay = Callable[[FloatVector, FloatVector], None]
RenderDebugIntersection = Callable[[FloatVector], None]


class RayContext(NamedTuple):
    level_grid: dict[tuple[int, int], Block]
    max_distance: float
    max_bounces: int
    tfov: Rect
    light_levels: LightLevel
    num_rays: dict[tuple[int, int], float]
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
    ray: Line, ctx: RayContext
) -> tuple[Optional[FloatVector], Optional[IntVector], Optional[Block]]:
    nearest_intersection = None
    nearest_distance = float("inf")
    nearest_block_pos = None
    nearest_block = None

    for pos in ray.blocks_along_line():
        block = ctx.level_grid.get(pos, None)
        if block is None:
            continue
        if nearest_block is None and block.blocks_light and ctx.tfov.contains(pos):
            for edge in block.edges_at(Vector(*pos)):
                intersection = edge.intersection(ray)
                if intersection:
                    dist = distance(ray.origin, intersection)
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_intersection = intersection
                        nearest_block_pos = pos
                        nearest_block = block

    return nearest_intersection, nearest_block_pos, nearest_block


def update_light_levels(
    ray: Line,
    origin: FloatVector,
    end: FloatVector,
    dst: float,
    energy: float,
    ctx: RayContext,
) -> None:
    for block_pos in ray.blocks_along_line():
        if block_pos in ctx.level_grid and not ctx.level_grid[block_pos].blocks_light:
            dist = distance(block_pos, origin)
            # ctx.rdi(block_pos, (128, 200, 200), dist)
            if dist >= distance(origin, end):
                return
            # light_level = 1 / (((dst + dist) / 3) ** 2)
            ctx.light_levels[block_pos] = min(
                1,
                max(
                    ctx.light_levels.get(block_pos, 0),
                    1 / (energy * (((dist + dst) / 2.5) ** 2)),
                ),
            )
            ctx.num_rays[block_pos] += 1
            # print(dst, dist, dst + dist, light_level, ctx.light_levels[block_pos])


def cast_ray(
    origin: FloatVector,
    direction: FloatVector,
    energy: float,
    bounces: int,
    dst: float,
    ctx: RayContext,
) -> int:
    if bounces > ctx.max_bounces or energy < 0.05:
        return 0
    ray = Line(origin, direction, restrict=(0, ctx.max_distance))
    # blocks_to_check = ctx.level_grid.get_blocks_in_range(origin, end_point)

    nearest_intersection, block_pos, block = find_nearest_intersection(ray, ctx)

    if nearest_intersection:
        # ctx.rdr(origin, nearest_intersection, (0, int(255 * energy), 0))
        update_light_levels(ray, origin, nearest_intersection, dst, energy, ctx)

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
                dst + distance(origin, reflected_origin),
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
    timer.tick("setup")
    light_levels: LightLevel = defaultdict(lambda: -1)
    light_source = (ppos.x, ppos.y)

    if not light_source:
        return light_levels

    num_rays = 200  # Number of rays to cast
    max_bounces = 3  # Maximum number of reflections
    tfov = Rect.from_vect_rect(fov)
    max_distance = tfov.half_diag

    ctx = RayContext(
        {p.to_tuple(): b for p, b in level.items()},
        max_distance,
        max_bounces,
        tfov,
        light_levels,
        defaultdict(lambda: 0),
        rdr,
        rdi,
        timer,
    )

    ray_directions = [
        (math.cos(a), math.sin(a))
        for a in [2 * math.pi * i / num_rays for i in range(num_rays)]
    ]

    timer.tick_end()
    for direction in ray_directions:
        cast_ray(light_source, direction, 1, 0, 0, ctx)

    # Normalize light levels
    timer.tick("cleanup")
    light_map: LightLevel = defaultdict(lambda: 0)
    max_light = max(light_levels.values(), default=1)
    max_rays = max(ctx.num_rays.values(), default=0)
    for pos in light_levels:
        light_levels[pos] /= max_light
        light_map[pos] = (light_levels[pos]) ** (1 - (ctx.num_rays[pos] / max_rays))
        # rdi(
        #     add_tuples(pos, (0.25, 0.25)),
        #     (200, 200, 200),
        #     (2 - (ctx.num_rays[pos] / max_rays)) * 5,
        # )
        # rdi(
        #     add_tuples(pos, (0.5, 0.5)),
        #     (200, 200, 255),
        #     1 / (light_levels[pos] ** 2 * 10),
        # )
    max_lights = max(light_map.values(), default=1)
    for pos in light_map:
        light_map[pos] /= max_lights
    timer.tick_end()
    timer.tick_end()
    timer.end_run()
    return light_map
