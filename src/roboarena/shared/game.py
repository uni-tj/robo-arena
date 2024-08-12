import logging
from abc import ABC
from collections.abc import Sequence
from typing import TYPE_CHECKING

from pygame import Rect

from roboarena.shared.entity import Entity
from roboarena.shared.types import EntityId

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import Level

logger = logging.getLogger(f"{__name__}")


class GameState(ABC):
    entites: dict[EntityId, Entity]
    level: "Level"

    def collisions(self, rect: Rect) -> tuple[Sequence[Entity], bool]:
        """Get the colliding entities and whether it collides with a wall"""
        colliding_entities = list[Entity]()
        for entity in self.entites.values():
            if rect.colliderect(entity.hitbox):
                colliding_entities.append(entity)
        return (colliding_entities, False)
