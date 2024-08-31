import random
from typing import TYPE_CHECKING, Any, TypeGuard

import pygame
from attrs import define, field

from roboarena.server.entity import (
    ServerDoorEntity,
    ServerEnemyRobot,
    ServerPlayerRobot,
)
from roboarena.server.level_generation.level_generator import BlockPosition
from roboarena.shared.types import DeathEvent, basic_weapon
from roboarena.shared.util import frame_cache_method
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.server import GameState
    from roboarena.shared.entity import Entity
type PlayerPosition = Vector[float]


def sample[T](iter: set[T], k: int) -> set[T]:
    return set(random.sample(list(iter), k))


def is_player(e: Any) -> TypeGuard[ServerPlayerRobot]:
    return isinstance(e, ServerPlayerRobot)


@define(eq=False)
class Room:
    _game: "GameState"
    _floors: set[BlockPosition]
    _doors: set[BlockPosition]
    _door_entities: list[ServerDoorEntity] = field(init=False)

    _started: bool = field(default=False, init=False)
    _enemies_alive: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._door_entities = list(
            ServerDoorEntity(self._game, pos + 0.5, True) for pos in self._doors
        )
        for door in self._door_entities:
            self._game.create_entity(door)

    def tick(self) -> None:
        if self._started:
            return
        players = (e for e in self._game.entities.values() if is_player(e))
        if any(self._is_in_room(e) for e in players):
            self.on_start()

    def on_start(self) -> None:
        print("on_start")
        self._started = True
        # close doors
        for door in self._door_entities:
            door.open.set(False)

        free_floors = set(self._floors)
        # port all players into room
        players = list(e for e in self._game.entities.values() if is_player(e))
        player_in_room = next(e for e in players if self._is_in_room(e))
        for player in players:
            if not self._is_in_room(player):
                new_ori = Vector.zero().to_float()
                player.motion.set((player_in_room.position, new_ori))
            free_floors -= set(self._game.colliding_blocks(player))

        # spawn enemies
        NUM_ENEMIES = min(len(free_floors), 1)
        self._enemies_alive = NUM_ENEMIES
        enemy_entities = list(
            ServerEnemyRobot(
                self._game,
                100,
                (pos.to_float(), Vector.zero().to_float()),
                pygame.Color(0, 0, 0),
                basic_weapon,
            )
            for pos in sample(free_floors, k=NUM_ENEMIES)
        )
        for enemy in enemy_entities:
            enemy.events.add_listener(DeathEvent, lambda e: self.on_enemy_death())
            self._game.create_entity(enemy)

    def on_enemy_death(self) -> None:
        self._enemies_alive -= 1
        if self._enemies_alive == 0:
            self.on_end()

    def on_end(self) -> None:
        print("on_end")
        # open doors
        for door in self._door_entities:
            door.open.set(True)

    @frame_cache_method
    def _is_in_room(self, entity: "Entity") -> bool:
        return self._floors.issuperset(self._game.colliding_blocks(entity).keys())
