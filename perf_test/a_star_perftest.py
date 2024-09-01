import random

from roboarena.shared.utils.perf_tester import PerformanceTester
from roboarena.shared.utils.search import Grid, astar
from roboarena.shared.utils.vector import Vector


def gen_data() -> tuple[Vector[int], Vector[int], Grid]:
    size = random.randint(25, 100)
    grid: Grid = {}

    for y in range(size):
        for x in range(size):
            grid[Vector(x, y)] = random.choice([True, False, False])

    start = Vector(random.randint(0, size - 1), random.randint(0, size - 1))
    goal = Vector(random.randint(0, size - 1), random.randint(0, size - 1))

    grid[start] = True
    grid[goal] = True

    return start, goal, grid


def id[T](x: T) -> T:
    return x


if __name__ == "__main__":
    performance_tester = PerformanceTester(10_000, gen_data)

    performance_tester.add_function(
        "astar", lambda data: astar(data[0], data[1], data[2]), id
    )

    performance_tester.compare_performance()
