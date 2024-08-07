import logging
from abc import ABC
from collections.abc import Sequence

from pygame import Rect

from roboarena.server.level_generation.level_generator import Level
from roboarena.shared.entity import Entity
from roboarena.shared.game_ui import GameUI
from roboarena.shared.types import EntityId

logger = logging.getLogger(f"{__name__}")


class GameState(ABC):
    entites: dict[EntityId, Entity]
    level: Level
    game_ui: GameUI

    def collisions(self, rect: Rect) -> tuple[Sequence[Entity], bool]:
        """Get the colliding entities and whether it collides with a wall"""
        colliding_entities = list[Entity]()
        for entity in self.entites.values():
            if rect.colliderect(entity.hitbox):
                colliding_entities.append(entity)
        return (colliding_entities, False)
