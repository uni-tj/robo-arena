import logging
import random
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, TypeGuard

import pygame
from attrs import define, field

from roboarena.server.entity import (
    ServerDoorEntity,
    ServerEnemyRobot,
    ServerPlayerRobot,
)
from roboarena.server.level_generation.level_generator import BlockPosition
from roboarena.shared.constants import EnemyConstants
from roboarena.shared.types import CloseEvent, DeathEvent, OpenEvent, basic_weapon
from roboarena.shared.util import EventTarget, frame_cache_method
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.server import GameState
    from roboarena.shared.entity import Entity

logger = logging.getLogger(__name__)


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
    events: EventTarget[CloseEvent | OpenEvent] = field(factory=EventTarget, init=False)

    _started: bool = field(default=False, init=False)
    _enemies_alive: int = field(init=False)

    @property
    def doors(self) -> set[BlockPosition]:
        return self._doors

    @property
    def floors(self) -> set[BlockPosition]:
        return self._floors

    @property
    @frame_cache_method
    def room_enemies(self) -> Iterable[ServerEnemyRobot]:
        return [
            ent
            for ent in self._game.entities.values()
            if self._is_in_room(ent) and isinstance(ent, ServerEnemyRobot)
        ]

    @property
    @frame_cache_method
    def room_entities(self) -> Iterable["Entity"]:
        return [ent for ent in self._game.entities.values() if self._is_in_room(ent)]

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
        logger.info("starting room")
        self._started = True
        # close doors
        self.events.dispatch(CloseEvent())
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
        NUM_ENEMIES = min(len(free_floors), 2)
        self._enemies_alive = NUM_ENEMIES
        enemy_entities = [
            ServerEnemyRobot(
                self._game,
                EnemyConstants.START_HEALTH,
                (pos.to_float() + Vector(0.5, 0.5), Vector.zero().to_float()),
                pygame.Color(0, 0, 0),
                basic_weapon,
                self,
                15,
            )
            for pos in sample(free_floors, k=NUM_ENEMIES)
        ]
        for enemy in enemy_entities:
            enemy.events.add_listener(DeathEvent, lambda e: self.on_enemy_death())
            self._game.create_entity(enemy)

    def on_enemy_death(self) -> None:
        self._enemies_alive -= 1
        if self._enemies_alive == 0:
            self.on_end()

    def on_end(self) -> None:
        logger.info("ending room")
        # open doors
        self.events.dispatch(OpenEvent())
        for door in self._door_entities:
            door.open.set(True)

    @frame_cache_method
    def _is_in_room(self, entity: "Entity") -> bool:
        return self._floors.issuperset(self._game.colliding_blocks(entity).keys())
