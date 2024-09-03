import math
import random
from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, Mapping

import numpy as np
from numpy.typing import NDArray

from roboarena.server.level_generation.level_generator import BlockPosition
from roboarena.server.level_generation.wfc import Direction
from roboarena.shared.constants import PlayerConstants
from roboarena.shared.entity import EnemyRobot, PlayerRobot
from roboarena.shared.types import Marker, MarkerVect, Motion, PygameColor
from roboarena.shared.util import get_min_max, rect_space
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

    _SAMPLING_FACTOR = 1

    def __init__(self, room: "Room", game: "GameState"):
        self._game = game
        self._room = room

        def combined_force(x: list[float]) -> float:
            min_dist = min(x)
            return min_dist
            if min_dist <= 1:
                return min(1 / ((min_dist + 0.001) ** (1 / 3)), 4.5)
            return math.log(min_dist) + 1

        self._wpdm, self._wpgm = self.calculate_wall_distance_map(
            combined_force,
        )
        self._i = 0

    def _get_room_blocks(self) -> Iterable[BlockPosition]:
        return self._room.floors

    def _get_room_block_map(self) -> Mapping[BlockPosition, bool]:
        return {pos: True for pos in self._room.floors}

    def _get_nearest_player(self, enemy_pos: EntityPosition) -> "ServerPlayerRobot":
        players = [
            (player_id, player, (player.motion.get()[0] - enemy_pos).length())
            for player_id, player in self._game.players
        ]
        return min(players, key=lambda x: x[2])[1]

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
        scaled_walls = list(
            map(lambda x: x * self._SAMPLING_FACTOR, self.find_all_walls())
        )

        def scaling_neighbours(pos: BlockPosition) -> list[BlockPosition]:
            return [
                pos + pb
                for pb in rect_space(
                    Vector(self._SAMPLING_FACTOR, self._SAMPLING_FACTOR)
                )
            ]

        def concat(xs: list[list[BlockPosition]]) -> list[BlockPosition]:
            res: list[BlockPosition] = []
            for x in xs:
                res.extend(x)
            return res

        scaled_walls = concat(
            [scaling_neighbours(pos * self._SAMPLING_FACTOR) for pos in walls]
        )
        dims = (max_pos - min_pos) * self._SAMPLING_FACTOR
        wpdm = np.full(
            dims.to_tuple(),
            float("inf"),
            dtype=np.float64,
        )

        max_val = float("-inf")
        for x in range(dims.x):
            for y in range(dims.y):
                ssbp = Vector(x, y) + min_pos * self._SAMPLING_FACTOR
                val = f([(ssbp - wpos).length() for wpos in scaled_walls])
                wpdm[x, y] = val
                max_val = max_val if val < max_val else val
        wpdm[wpdm == float("inf")] = max_val
        wpgm: WallPositionGradientMap = list(map(lambda x: x, np.gradient(wpdm)))

        # markers = []
        # for x in range(dims.x):
        #     for y in range(dims.y):
        #         pos = Vector(x, y)
        #         gradient_x = wpgm[0][x, y]
        #         gradient_y = wpgm[1][x, y]
        #         # wpgm[0][x, y], wpgm[1][x, y]
        #         start_pos = Vector(x, y) / self._SAMPLING_FACTOR + min_pos
        #         end_pos = start_pos + Vector(gradient_x, gradient_y)
        #         markers.append(
        #             MarkVect(
        #                 start=start_pos, end=end_pos, color=PygameColor(128, 0, 255)
        #             )
        #         )
        # self._game.markvect(markers)
        return wpdm, wpgm

    def _calculate_wall_repulsion_force(self, pos: EntityPosition) -> Vector[float]:
        min_pos, _ = get_min_max(self.find_all_walls())
        grid_pos = ((pos - min_pos) * self._SAMPLING_FACTOR).round()

        try:

            gradient_x = self._wpgm[1][grid_pos.x, grid_pos.y]
            gradient_y = self._wpgm[0][grid_pos.x, grid_pos.y]
        except IndexError:
            return Vector.zero()

        grad = Vector(gradient_x, gradient_y)
        if grad.length() == 0:
            return grad
        fact = math.log(grad.length() + 1.0)
        ng = grad.normalize()
        return Vector(ng.x * fact, ng.y * fact)

    def _calculate_entity_repulsion_force(
        self, current_pos: EntityPosition
    ) -> Vector[float]:
        repulsion_force = Vector.zero()
        entities = list(self._room.room_entities) + list(
            map(lambda x: x[1], self._game.players)
        )

        for entity in entities:

            if isinstance(entity, (EnemyRobot, PlayerRobot)):
                entity_pos = entity.motion.get()[0]
            else:
                entity_pos = entity.position
            if entity_pos == current_pos:
                continue

            distance_vector = current_pos - entity_pos
            distance_vector = (
                Matrix2d.rot_matrix(random.uniform(0, 1.5)) * distance_vector
            )
            distance = distance_vector.length()

            if distance < 4.0:  # CONST: Repulsion radius
                factor = (
                    1.7 if isinstance(entity, EnemyRobot) else 1.9
                )  # Empirical Values
                force_magnitude = 1 / (distance / 4) ** factor
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
        enemy_pos, cur_velocity = enemy.motion.get()
        nearest_player = self._get_nearest_player(enemy_pos)

        player_pos: EntityPosition = nearest_player.motion.get()[0]

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
        combined_force += a_start_force * 1.5

        # Set Max Force Limit (Empirical Values)
        combined_force *= 0.15
        max_force = 2.5
        if combined_force.length() > max_force:
            combined_force = combined_force.normalize() * max_force

        acceleration = combined_force
        #
        self._i += 1
        # Mark Debug positions + Forces acting on enemies
        if self._i % 100 == 0:
            self._game.mark(
                [
                    Marker(enemy_pos, PygameColor.green()),
                ]
                + [Marker(pos.to_float(), PygameColor.grey()) for pos in path]
            )
            self._game.markvect(
                [
                    MarkerVect(
                        enemy_pos, enemy_pos + wall_force, PygameColor(255, 129, 0)
                    ),
                    MarkerVect(
                        enemy_pos, enemy_pos + entity_force, PygameColor(0, 255, 0)
                    ),
                    MarkerVect(
                        enemy_pos, enemy_pos + player_force, PygameColor(0, 0, 255)
                    ),
                    MarkerVect(
                        enemy_pos, enemy_pos + a_start_force, PygameColor(200, 200, 200)
                    ),
                    MarkerVect(
                        enemy_pos, enemy_pos + combined_force, PygameColor(0, 0, 255)
                    ),
                ]
            )
        # Update Velocity + prevent moving into walls->sliding along walls
        new_velocity = cur_velocity * (1 - PlayerConstants.DECELERATE) + acceleration
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

    # def check_shooting(self, enemy:EnemyRobot)
