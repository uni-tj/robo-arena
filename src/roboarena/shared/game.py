import logging
from abc import ABC
from collections.abc import Iterable
from typing import Literal, overload

from roboarena.server.level_generation.level_generator import Level
from roboarena.shared.block import wall
from roboarena.shared.entity import Entity
from roboarena.shared.game_ui import GameUI
from roboarena.shared.types import EntityId
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


class GameState(ABC):
    env: Literal["server"] | Literal["client"]
    entities: dict[EntityId, Entity]
    level: Level
    game_ui: GameUI

    @overload
    def collidingEntities(self, collider: Entity) -> Iterable[Entity]: ...

    @overload
    def collidingEntities(self, collider: Rect) -> Iterable[Entity]: ...

    def collidingEntities(self, collider: Rect | Entity) -> Iterable[Entity]:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        entities = self.entities.values()
        return (
            _
            for _ in entities
            if _.collision.hitbox.overlaps(rect) and _ is not collider
        )

    @overload
    def collidingWalls(self, collider: Entity) -> bool: ...

    @overload
    def collidingWalls(self, collider: Rect) -> bool: ...

    def collidingWalls(self, collider: Rect | Entity) -> bool:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        for x in range(rect.top_left.floor().x, rect.bottom_right.ceil().x):
            for y in range(rect.top_left.floor().y, rect.bottom_right.ceil().y):
                xy = Vector(x, y)
                if xy in self.level and self.level[xy] is wall:
                    return True
        return False
