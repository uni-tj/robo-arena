from abc import ABC
from collections.abc import Sequence

from pygame import Rect

from shared.entity import Entity
from shared.types import EntityId


class GameState(ABC):
    _entites: dict[EntityId, Entity]

    def collisions(self, rect: Rect) -> tuple[Sequence[Entity], bool]:
        """Get the colliding entities and whether it collides with a wall"""
        colliding_entities = list[Entity]()
        for entity in self._entites.values():
            if rect.colliderect(entity.hitbox):
                colliding_entities.append(entity)
        return (colliding_entities, False)
