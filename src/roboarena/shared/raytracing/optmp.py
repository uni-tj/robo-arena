import math
import multiprocessing
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Optional

from roboarena.shared.block import Block
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import FieldOfView

type Level = dict[Vector[int], "Block"]
type LightLevel = dict[Vector[int], float]
type RenderDebugRay = Callable[[Vector[float], Vector[float]], None]
type RenderDebugIntersection = Callable[[Vector[float]], None]

type BlockChunk = list[tuple[Vector[int], Block]]


class Grid:
    grid: dict[tuple[int, int], BlockChunk]

    def __init__(self, level: Level, cell_size: int = 5):
        self.cell_size = cell_size
        self.grid = {}
        for pos, block in level.items():
            cell = (pos.x // cell_size, pos.y // cell_size)
            self.grid[cell].append((pos, block))

    def get_blocks_in_range(
        self, start: Vector[float], end: Vector[float]
    ) -> BlockChunk:
        start_cell = (int(start.x) // self.cell_size, int(start.y) // self.cell_size)
        end_cell = (int(end.x) // self.cell_size, int(end.y) // self.cell_size)

        blocks: BlockChunk = []
        for x in range(
            min(start_cell[0], end_cell[0]), max(start_cell[0], end_cell[0]) + 1
        ):
            for y in range(
                min(start_cell[1], end_cell[1]), max(start_cell[1], end_cell[1]) + 1
            ):
                if (x, y) in self.grid:
                    blocks.extend(self.grid[(x, y)])
        return blocks


class Line:
    def __init__(
        self,
        origin: Vector[float],
        direction: Vector[float],
        restrict: Optional[tuple[float, float]] = None,
    ) -> None:
        self.origin = origin
        self.direction = direction.normalize()
        self._restrict = restrict

    def intersection(self, other: "Line") -> Optional[Vector[float]]:
        d = self.direction
        e = other.direction
        o = self.origin
        p = other.origin
        det = d.x * e.y - d.y * e.x
        if abs(det) < 1e-6:
            return None
        t = ((p.x - o.x) * e.y - (p.y - o.y) * e.x) / det
        u = ((p.x - o.x) * d.y - (p.y - o.y) * d.x) / det
        if self._restrict and not (self._restrict[0] <= t <= self._restrict[1]):
            return None
        if other._restrict and not (other._restrict[0] <= u <= other._restrict[1]):
            return None
        return o + d * t


def cast_ray(args):
    level_grid, origin, direction, energy, max_distance, fov = args
    ray = Line(origin, direction, (0, max_distance))
    light_levels = {}

    blocks_to_check = level_grid.get_blocks_in_range(
        origin, origin + direction * max_distance
    )

    nearest_intersection = None
    nearest_distance = float("inf")

    for pos, block in blocks_to_check:
        if block.render_above_entities and fov.contains(pos.to_float()):
            for edge in block.edges_at(pos):
                intersection = edge.intersection(ray)
                if intersection:
                    distance = (intersection - origin).length()
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_intersection = (intersection, pos, block)

    current_pos = origin
    step = direction.normalize() * 0.5
    while (current_pos - origin).length() <= nearest_distance:
        block_pos = current_pos.to_int()
        if block_pos in dict(blocks_to_check):
            distance = (current_pos - origin).length()
            light_level = energy * (1 - distance / nearest_distance)
            light_levels[block_pos] = max(light_levels.get(block_pos, 0), light_level)
        current_pos += step

    return light_levels


def calculate_light(
    level: Level,
    ppos: Vector[float],
    fov: "FieldOfView",
    rdr: RenderDebugRay,
    rdi: RenderDebugIntersection,
) -> LightLevel:
    light_source = ppos
    if not light_source:
        return {}

    level_grid = Grid(level)
    num_rays = 50  # Reduced number of rays
    max_distance = 20  # Maximum ray distance

    ray_args = [
        (
            level_grid,
            light_source,
            Vector.from_angle(2 * math.pi * i / num_rays),
            1,
            max_distance,
            fov,
        )
        for i in range(num_rays)
    ]

    with multiprocessing.Pool() as pool:
        results = pool.map(cast_ray, ray_args)

    light_levels = {}
    for result in results:
        for pos, level in result.items():
            light_levels[pos] = max(light_levels.get(pos, 0), level)

    # Normalize light levels
    max_light = max(light_levels.values(), default=1)
    for pos in light_levels:
        light_levels[pos] /= max_light

    return light_levels
