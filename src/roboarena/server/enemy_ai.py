import math
import random
from collections import defaultdict, deque
from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, Mapping, Optional

import numpy as np
from numpy.typing import NDArray

from roboarena.server.level_generation.level_generator import BlockPosition
from roboarena.server.level_generation.wfc import Direction
from roboarena.shared.constants import PlayerConstants
from roboarena.shared.entity import Bullet
from roboarena.shared.types import EntityId, Motion
from roboarena.shared.util import get_min_max
from roboarena.shared.utils.search import astar
from roboarena.shared.utils.vector import Matrix2d, Vector

if TYPE_CHECKING:
    from roboarena.server.entity import ServerEnemyRobot, ServerPlayerRobot
    from roboarena.server.room import Room
    from roboarena.server.server import GameState
    from roboarena.shared.entity import EnemyRobotMoveCtx

type EntityPosition = Vector[float]
type WallPositions = list[BlockPosition]
type WallPositionDistanceMap = NDArray[np.float64]
type WallPositionGradientMap = list[NDArray[np.float64]]


class EnemyAi:
    _wpdm: WallPositionDistanceMap
    _wpgm: WallPositionGradientMap
    _player_poss_map: defaultdict[EntityId, deque[EntityPosition]]

    _difficulty: float

    def __init__(self, room: "Room", game: "GameState", difficulty: float):
        # difficulty
        self._game = game
        self._room = room

        def combined_force(x: list[float]) -> float:
            min_dist = min(x)
            return 1 / math.exp(min_dist)

        self._wpdm, self._wpgm = self.calculate_wall_distance_map(
            combined_force,
        )
        self._i = 0
        self._player_poss_map = defaultdict(lambda: deque(maxlen=60))
        self._difficulty = difficulty + 5

    def _get_room_blocks(self) -> Iterable[BlockPosition]:
        return self._room.floors

    def _get_room_block_map(self) -> Mapping[BlockPosition, bool]:
        return {pos: True for pos in self._room.floors}

    def _get_players_in_room(self) -> Iterable[tuple[EntityId, "ServerPlayerRobot"]]:
        return (
            (eid, player)
            for eid, player in self._game.players
            if self._room._is_in_room(player)
        )

    def _get_nearest_player(
        self, enemy_pos: EntityPosition
    ) -> Optional[tuple[EntityId, "ServerPlayerRobot"]]:
        players = [
            (player_id, player, (player.motion.get()[0] - enemy_pos).length())
            for player_id, player in self._get_players_in_room()
        ]
        if len(players) == 0:
            return None
        np = min(players, key=lambda x: x[2])
        return np[0], np[1]

    def find_all_walls(self) -> WallPositions:
        """Find all walls in the room that are adjacent to the room"""
        blocks = set(self._get_room_blocks())
        return [
            pos + dir.value
            for dir in Direction
            for pos in blocks
            if pos + dir.value not in blocks
        ]

    def calculate_wall_distance_map(
        self, f: Callable[[list[float]], float]
    ) -> tuple[WallPositionDistanceMap, WallPositionGradientMap]:
        """Calculates the wall distance map and its gradient"""
        # walls = map(lambda x: x * Sampling_factor, self.find_all_walls())
        walls = self.find_all_walls()
        min_pos, max_pos = get_min_max(walls)
        max_pos += Vector(1, 1)
        dims = max_pos - min_pos
        wpdm = np.full(
            dims.to_tuple(),
            float("inf"),
            dtype=np.float64,
        )

        max_val = float("-inf")
        for x in range(dims.x):
            for y in range(dims.y):
                ssbp = Vector(x, y) + min_pos
                val = f([(ssbp - wpos).length() for wpos in walls])
                wpdm[x, y] = val
                max_val = max_val if val < max_val else val
        wpdm[wpdm == float("inf")] = max_val
        wpgm: WallPositionGradientMap = list(map(lambda x: -x, np.gradient(wpdm)))

        # markers = []
        # for x in range(dims.x):
        #     for y in range(dims.y):
        #         pos = Vector(x, y)
        #         gradient_x = wpgm[0][x, y]
        #         gradient_y = wpgm[1][x, y]
        #         # wpgm[0][x, y], wpgm[1][x, y]
        #         start_pos = Vector(x, y) + min_pos
        #         end_pos = start_pos + Vector(gradient_x, gradient_y)
        #         markers.append(
        #             MarkerVect(
        #                 start=start_pos, end=end_pos, color=PygameColor(128, 0, 255)
        #             )
        #         )
        # self._game.markvect(markers)
        return wpdm, wpgm

    def _calculate_wall_repulsion_force(self, pos: EntityPosition) -> Vector[float]:
        min_pos, _ = get_min_max(self.find_all_walls())

        grid_pos = pos - min_pos

        ix, iy = int(grid_pos.x), int(grid_pos.y)
        fx, fy = grid_pos.x - ix, grid_pos.y - iy

        grid_x = [
            [
                self._wpgm[0][
                    max(0, min(ix + i, self._wpgm[0].shape[0] - 1)),
                    max(0, min(iy + j, self._wpgm[0].shape[1] - 1)),
                ]
                for j in range(-1, 3)
            ]
            for i in range(-1, 3)
        ]

        grid_y = [
            [
                self._wpgm[1][
                    max(0, min(ix + i, self._wpgm[1].shape[0] - 1)),
                    max(0, min(iy + j, self._wpgm[1].shape[1] - 1)),
                ]
                for j in range(-1, 3)
            ]
            for i in range(-1, 3)
        ]

        gradient_x = bicubic_interpolation(grid_x, fx, fy)
        gradient_y = bicubic_interpolation(grid_y, fx, fy)

        return Vector(gradient_x, gradient_y)

    def _calculate_entity_repulsion_force(
        self, current_pos: EntityPosition
    ) -> Vector[float]:
        repulsion_force = Vector.zero()
        entities = list(self._room.room_entities) + list(
            map(lambda x: x[1], self._game.players)
        )

        for entity in entities:
            factor = 1.5
            entity_pos = entity.position
            distance_vector = current_pos - entity_pos
            distance = distance_vector.length()
            if isinstance(entity, Bullet):
                factor = 1 * self._difficulty
                if not entity.friendly:
                    continue
                repulsion_force += distance_vector
                distance_vector = (
                    Matrix2d.rot_matrix(random.uniform(0, math.pi)) * distance_vector
                )
            # distance /= 5

            if 0 < distance < 4.5:  # CONST: Repulsion radius
                # force_magnitude = 1 / (distance / 4.5) ** (1 / factor)
                distance = max(0.01, distance)
                force_magnitude = min(1 / (distance / 6 + 0.001) ** factor, 4.5)
                repulsion_force += distance_vector.normalize() * force_magnitude

        return repulsion_force

    def _calculate_player_attraction_force(
        self, enemy_pos: EntityPosition, player_pos: EntityPosition
    ) -> Vector[float]:
        return (player_pos - enemy_pos).normalize()

    def update_enemy_position(
        self, current: Motion, enemy: "ServerEnemyRobot", ctx: "EnemyRobotMoveCtx"
    ) -> Motion:
        (dt,) = ctx
        enemy_pos, cur_velocity = current
        np = self._get_nearest_player(enemy_pos)
        if np is None:
            return current

        _, nearest_player = np

        player_pos = nearest_player.motion.get()[0]

        # Calculate forces
        wall_force = self._calculate_wall_repulsion_force(enemy_pos) * 1.5
        entity_force = self._calculate_entity_repulsion_force(enemy_pos) * 1
        player_force = (
            self._calculate_player_attraction_force(enemy_pos, player_pos) * 1.0
        )

        combined_force = wall_force + entity_force + player_force
        mod_player_pos = player_pos
        if cur_velocity.length() < 1:
            mod_player_pos += Vector.random_unif(-3, 3).round()
        # to improve pathfinding use astar to improve the pathfinding of the player
        path = astar(
            enemy_pos.floor(), mod_player_pos.floor(), self._get_room_block_map()
        )
        if len(path) < 2:
            a_start_force = Vector.zero()
        else:
            a_start_force = (path[1] + Vector(0.49, 0.49)) - enemy_pos
        combined_force += a_start_force * 0.5

        # Set Max Force Limit (Empirical Values)
        combined_force *= 0.15  # * math.sqrt(math.log(self._difficulty))
        max_force = 3
        if combined_force.length() > max_force:
            combined_force = combined_force.normalize() * max_force

        # Mark Debug positions + Forces acting on enemies
        self._i += 1
        if self._i % 10 == 0:
            # self._game.mark(
            #     [
            #         Marker(enemy_pos, PygameColor.green()),
            #     ]
            #     + [Marker(pos.to_float(), PygameColor.grey()) for pos in path]
            # )
            # self._game.markvect(
            #     [
            #         MarkerVect(
            #             enemy_pos, enemy_pos + wall_force, PygameColor(255, 129, 0)
            #         ),
            #         MarkerVect(
            #             enemy_pos, enemy_pos + entity_force, PygameColor(0, 255, 0)
            #         ),
            #         MarkerVect(
            #             enemy_pos, enemy_pos + player_force, PygameColor(0, 0, 255)
            #         ),
            #         MarkerVect(
            #             enemy_pos, enemy_pos
            # + a_start_force, PygameColor(200, 200, 200)
            #         ),
            #         MarkerVect(
            #             enemy_pos, enemy_pos + combined_force, PygameColor(0, 0, 255)
            #         ),
            #     ]
            # )
            pass
        # Update Velocity + prevent moving into walls->sliding along walls
        new_velocity = (
            cur_velocity * (1 - PlayerConstants.DECELERATE * 3) + combined_force
        )
        if new_velocity.length() < 0.1:
            new_velocity = Vector(0.0, 0.0)
        new_position = enemy_pos + new_velocity * dt
        if not self._game.blocking(enemy.collision.hitbox_at(new_position), "robot"):
            return (new_position, new_velocity)
        new_velocity_x = new_velocity * Vector(1, 0)
        new_position_x = enemy_pos + new_velocity_x * dt
        if not self._game.blocking(enemy.collision.hitbox_at(new_position_x), "robot"):
            return (new_position_x, new_velocity_x)
        new_velocity_y = new_velocity * Vector(0, 1)
        new_position_y = enemy_pos + new_velocity_y * dt
        if not self._game.blocking(enemy.collision.hitbox_at(new_position_y), "robot"):
            return (new_position_y, new_velocity_y)
        return (enemy_pos, Vector(0.0, 0.0))

    def _track_players(self) -> None:
        for eid, player in self._get_players_in_room():
            self._player_poss_map[eid].append(player.motion.get()[0])

    def shoot(
        self, current: Motion, enemy: "ServerEnemyRobot", ctx: "EnemyRobotMoveCtx"
    ) -> None:
        self._track_players()
        bullet_speed = enemy.weapon.bullet_speed
        max_prediction_time = 20.0
        accuracy_factor = 1.0

        enemy_pos, _ = current
        _np = self._get_nearest_player(enemy_pos)
        if _np is None:
            return
        pid, _ = _np
        positions = self._player_poss_map[pid]
        (dt,) = ctx

        if len(positions) < 2:
            return

        current_pos = positions[-1]
        prev_pos = positions[-2]
        velocity = (current_pos - prev_pos) / dt

        def predict_position(t: float) -> EntityPosition:
            return current_pos + velocity * t

        def time_to_hit(t: float) -> float:
            predicted_pos = predict_position(t)
            distance = (predicted_pos - enemy_pos).length()
            return distance / (bullet_speed + 0.1) - t

        # Using newton approximation
        t: float = 0

        for _ in range(25):
            t -= time_to_hit(t) / (
                Vector.dot(velocity, velocity) / (bullet_speed + 0.1) - 1
            )

        if 0 < t < max_prediction_time:
            aim_position = predict_position(t)

            inaccuracy = Vector.random_unif(0, accuracy_factor)
            aim_position += inaccuracy

            direction = aim_position - enemy_pos

            if random.random() < ((1 / 60) * self._difficulty):
                enemy.weapon.shoot(direction)
                pass

        # self._game.mark(markers)


def cubic_interpolation(p: list[float], x: float) -> float:
    """Perform cubic interpolation."""
    return p[1] + 0.5 * x * (
        p[2]
        - p[0]
        + x
        * (
            2.0 * p[0]
            - 5.0 * p[1]
            + 4.0 * p[2]
            - p[3]
            + x * (3.0 * (p[1] - p[2]) + p[3] - p[0])
        )
    )


def bicubic_interpolation(p: list[list[float]], x: float, y: float) -> float:
    """Perform bicubic interpolation."""
    return cubic_interpolation([cubic_interpolation(row, y) for row in p], x)


def get_grid_values(
    start: Vector[int], size: int, get_value: Callable[[Vector[int]], float]
) -> list[list[float]]:
    """Generate a grid of values using the provided function."""
    return [[get_value(start + Vector(i, j)) for j in range(size)] for i in range(size)]
