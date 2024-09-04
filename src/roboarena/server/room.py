import logging
import math
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
from roboarena.shared.constants import DIFFICULTY, EnemyConstants, WeaponConstants
from roboarena.shared.types import CloseEvent, DeathEvent, OpenEvent, Weapon
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
    _waves_remaining: int = field(init=False)
    _alien_weapon: Weapon = field(init=False)
    _free_floors: set[BlockPosition] = field(init=False)

    @property
    def doors(self) -> set[BlockPosition]:
        return self._doors

    @property
    def floors(self) -> set[BlockPosition]:
        return self._floors

    @property
    def difficulty(self) -> float:
        doors = list(self._doors)
        return Vector.sum_vectors(doors).length() / 25  # type:ignore

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
        self._waves_remaining = int(
            math.sqrt((self.difficulty / DIFFICULTY.Weapon_Mod) ** 1.2)
        )
        self._alien_weapon = Weapon(
            weapon_speed=max(
                WeaponConstants.WEAPON_SPEED - self.difficulty % DIFFICULTY.Weapon_Mod,
                0.5,
            ),
            bullet_speed=WeaponConstants.BULLET_SPEED
            + self.difficulty % DIFFICULTY.Weapon_Mod,
            bullet_strength=int(
                WeaponConstants.BULLET_Strength
                + self.difficulty // DIFFICULTY.Weapon_Mod
            ),
        )
        self._free_floors = free_floors

        # spawn enemies
        self.spawn_enemies(free_floors)

    def spawn_enemies(self, free_floors: set[BlockPosition]):
        print("spawn_enemies")
        NUM_ENEMIES = min(len(free_floors), 2)
        self._enemies_alive = NUM_ENEMIES
        enemy_entities = [
            ServerEnemyRobot(
                self._game,
                int(EnemyConstants.START_HEALTH + self.difficulty),
                (pos.to_float() + Vector(0.5, 0.5), Vector.zero().to_float()),
                pygame.Color(0, 0, 0),
                self._alien_weapon,
                self,
                self.difficulty,
            )
            for pos in sample(free_floors, k=NUM_ENEMIES)
        ]
        for enemy in enemy_entities:
            enemy.events.add_listener(DeathEvent, lambda e: self.on_enemy_death())
            self._game.create_entity(enemy)

    def on_enemy_death(self) -> None:
        self._enemies_alive -= 1

        if self._enemies_alive == 0:
            if self._waves_remaining >= 0:
                self.spawn_enemies(self._free_floors)
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
