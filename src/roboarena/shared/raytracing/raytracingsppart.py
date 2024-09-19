import math
from typing import TYPE_CHECKING, Callable

from roboarena.server.level_generation.tileset import end_room, floor, floor_room
from roboarena.shared.block import Block
from roboarena.shared.raytracing.util import Line
from roboarena.shared.utils.timer import Timer
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

    def __init__(self, level: Level, cell_size: int = 3):
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


def calculate_light(
    level: Level,
    ppos: Vector[float],
    fov: "FieldOfView",
    rdr: RenderDebugRay,
    rdi: RenderDebugIntersection,
    timer: Timer,
) -> LightLevel:
    _timer = timer
    _timer.tick("total")
    # Returns all blocks that are illuminated by the light source and their light level

    light_levels: dict[Vector[int], float] = {}
    light_source = ppos
    # = next(
    #     (pos for pos, block in level.items() if block.is_light_source), None
    # )

    if not light_source:
        return light_levels
    max_distance = fov.half_diag
    num_rays = 100  # Number of rays to cast
    max_bounces = 2  # Maximum number of reflections
    level_grid = Grid(level)

    def cast_ray(
        origin: Vector[float],
        direction: Vector[float],
        energy: float,
        bounces: int,
        rdr,
        rdi,
    ):
        if bounces > max_bounces or energy < 0.05:
            return

        ray = Line(origin, direction, restrict=(0, float("inf")))

        # blocks_to_check = level_grid.get_blocks_in_range(
        #     origin, origin + direction * max_distance
        # )
        blocks_to_check = level.items()
        # Find the nearest intersection
        nearest_intersection = None
        nearest_distance = float("inf")
        _timer.tick("find_intersections")
        for pos, block in blocks_to_check:
            if block.render_above_entities and fov.contains(
                pos.to_float()
            ):  # TODO check if this is correct
                for edge in block.edges_at(pos):
                    _timer.tick("cacl_intersect")
                    intersection = edge.intersection(ray)
                    _timer.tick_end()
                    # edge.render(rdr)
                    if intersection:
                        assert block is not floor
                        rdi(intersection)
                        distance = (intersection - origin).length()
                        rdi(pos, (255, 0, 100))
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_intersection = (intersection, pos, block)
        _timer.tick_end()
        _timer.tick("reflections")
        _timer.tick_end()
        if nearest_intersection:
            _timer.tick("update_light")
            intersection, block_pos, block = nearest_intersection
            rdr(origin, intersection, (0, 200, 0))

            # Update light level for the intersected block
            current_pos = origin
            step = direction.normalize() * 0.5  # Small step size
            while (current_pos - origin).length() <= nearest_distance:
                block_pos = current_pos.to_int()
                if block_pos in level:
                    distance = (current_pos - origin).length()
                    light_level = energy * (1 - distance / nearest_distance)
                    light_levels[block_pos] = max(
                        light_levels.get(block_pos, 0), light_level
                    )
                current_pos += step
            _timer.tick_end()
            # _timer.tick("reflections")
            # Handle reflection
            if block.reflectivity > 0:
                normal = block.get_normal(block_pos, intersection)
                reflected_direction = direction - normal * 2 * Vector.dot(
                    direction, normal
                )
                reflected_energy = energy * block.reflectivity
                cast_ray(
                    intersection + reflected_direction * 0.01,
                    reflected_direction,
                    reflected_energy,
                    bounces + 1,
                    rdr,
                    rdi,
                )
            # _timer.tick_end()

    # Cast rays in random directions
    a_step = 2 * math.pi / num_rays
    for i in range(num_rays):

        angle = a_step * i
        direction = Vector.from_angle(angle)
        r = Line(ppos, direction, restrict=(0, 10))

        def col(i):
            c = int(255 * ((i) / num_rays))
            return c

        def rdra(s, e, c=None):
            if c is None:
                rdr(s, e, (255, col(i), 0))
            else:

                rdr(s, e, c)

        def rdia(s, c=None):
            rdi(s, (255, col(i), 0))

        r.render(rdra)
        cast_ray(light_source, direction, 1, 0, rdra, rdia)

    # Normalize light levels
    max_light = max(light_levels.values(), default=1)
    for pos in light_levels:
        light_levels[pos] /= max_light
    _timer.tick_end()
    return light_levels
