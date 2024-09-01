import heapq
from collections.abc import Iterable
from dataclasses import dataclass
from functools import total_ordering
from typing import Mapping

from roboarena.server.level_generation.wfc import Direction
from roboarena.shared.utils.vector import Vector


@total_ordering
@dataclass
class HeapItem:
    key: int
    pos: Vector[int]

    def __lt__(self, o: "HeapItem") -> bool:
        return self.key < o.key

    def to_tuple(self):
        return (self.key, self.pos)


# type HeapItem = tuple[int, Vector[int]]
type Grid = Mapping[Vector[int], bool]
type ScoreMapping = Mapping[Vector[int], int]


def manhattan_heuristic(node: Vector[int], goal: Vector[int]) -> int:
    return abs(node.x - goal.x) + abs(node.x - goal.x)


def astar(start: Vector[int], goal: Vector[int], grid: Grid) -> list[Vector[int]]:
    if start not in grid or not grid[start]:
        return []
    open_list: list[HeapItem] = []
    heapq.heappush(open_list, HeapItem(0, start))
    came_from: dict[Vector[int], Vector[int]] = {}
    g_score: ScoreMapping = {start: 0}
    f_score: ScoreMapping = {start: manhattan_heuristic(start, goal)}

    while open_list:
        _, current = heapq.heappop(open_list).to_tuple()

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_heuristic(
                    neighbor, goal
                )
                heapq.heappush(open_list, HeapItem(f_score[neighbor], neighbor))

    return []


def reconstruct_path(
    came_from: dict[Vector[int], Vector[int]], current: Vector[int]
) -> list[Vector[int]]:
    path: list[Vector[int]] = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def get_neighbors(pos: Vector[int], grid: Grid) -> Iterable[Vector[int]]:
    for dir in Direction:
        dv = dir.value
        neighbor = dv + pos
        if neighbor in grid and grid[neighbor]:
            yield neighbor
