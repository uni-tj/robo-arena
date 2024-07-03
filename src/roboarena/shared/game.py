import logging
from abc import ABC
from collections.abc import Iterable
from typing import overload

from roboarena.shared.block import WallBlock
from roboarena.shared.entity import Entity
from roboarena.shared.types import EntityId, Level
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


class GameState(ABC):
    entities: dict[EntityId, Entity]
    level: Level

    @overload
    def collidingEntities(self, collider: Entity) -> Iterable[Entity]: ...

    @overload
    def collidingEntities(self, collider: Rect) -> Iterable[Entity]: ...

    def collidingEntities(self, collider: Rect | Entity) -> Iterable[Entity]:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        entities = self.entities.values()
        return filter(lambda _: _.collision.hitbox.overlaps(rect), entities)

    @overload
    def collidingWalls(self, collider: Entity) -> bool: ...

    @overload
    def collidingWalls(self, collider: Rect) -> bool: ...

    def collidingWalls(self, collider: Rect | Entity) -> bool:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        for x in range(rect.top_left.floor().x, rect.bottom_right.ceil().x):
            for y in range(rect.top_left.floor().y, rect.bottom_right.ceil().y):
                xy = Vector(x, y)
                if xy in self.level and isinstance(self.level[xy], WallBlock):
                    return True
        return False
