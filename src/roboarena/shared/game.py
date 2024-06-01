from abc import ABC
from collections.abc import Sequence

from pygame import Rect

from roboarena.shared.entity import Entity
from roboarena.shared.types import EntityId, Level


class GameState(ABC):
    entites: dict[EntityId, Entity]
    level: Level

    def collisions(self, rect: Rect) -> tuple[Sequence[Entity], bool]:
        """Get the colliding entities and whether it collides with a wall"""
        colliding_entities = list[Entity]()
        for entity in self.entites.values():
            if rect.colliderect(entity.hitbox):
                colliding_entities.append(entity)
        return (colliding_entities, False)
