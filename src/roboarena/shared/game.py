import logging
from abc import ABC
from collections.abc import Iterable
from functools import cached_property
from typing import TYPE_CHECKING, Literal, overload

from roboarena.shared.block import wall
from roboarena.shared.entity import Entity
from roboarena.shared.game_ui import GameUI
from roboarena.shared.types import EntityId, QuitEvent, StartFrameEvent
from roboarena.shared.util import EventTarget, frame_cache_method, rect_space
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import BlockPosition, Level
    from roboarena.shared.block import Block

logger = logging.getLogger(f"{__name__}")


class GameState(ABC):
    env: Literal["server"] | Literal["client"]
    entities: dict[EntityId, Entity]
    level: "Level"
    events: EventTarget[QuitEvent | StartFrameEvent]
    game_ui: GameUI

    @cached_property
    def _game(self) -> "GameState":
        """Required for `frame_cache_method`"""
        return self

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

    @frame_cache_method
    def colliding_blocks(
        self, collider: Rect | Entity
    ) -> dict["BlockPosition", "Block"]:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        return {
            p: self.level[p]
            for p in rect_space(rect.top_left.floor(), rect.bottom_right.floor())
        }
