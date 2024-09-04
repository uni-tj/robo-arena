import logging
from abc import ABC
from collections.abc import Iterable
from functools import cached_property
from typing import TYPE_CHECKING, Literal, overload

from roboarena.shared.entity import Entity
from roboarena.shared.game_ui import GameUI
from roboarena.shared.types import EntityId, QuitEvent, StartFrameEvent
from roboarena.shared.util import (
    EventTarget,
    change_exception,
    frame_cache_method,
    rect_space_at,
)
from roboarena.shared.utils.rect import Rect

if TYPE_CHECKING:
    from roboarena.server.level_generation.level_generator import BlockPosition, Level
    from roboarena.shared.block import Block

logger = logging.getLogger(f"{__name__}")


class OutOfLevelError(Exception):
    """Thrown when an entity collides with blocks that are not yet generated"""


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

    def blocking(
        self, collider: Rect | Entity, mode: Literal["robot"] | Literal["bullet"]
    ) -> bool:
        return any(
            (mode == "robot" and e.blocks_robot)
            or (mode == "bullet" and e.blocks_bullet)
            for e in self.collidingEntities(collider)
        ) or any(
            (mode == "robot" and b.blocks_robot)
            or (mode == "bullet" and b.blocks_bullet)
            for b in self.colliding_blocks(collider).values()
        )

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

    @frame_cache_method
    def colliding_blocks(
        self, collider: Rect | Entity
    ) -> dict["BlockPosition", "Block"]:
        rect = collider.collision.hitbox if isinstance(collider, Entity) else collider
        with change_exception(KeyError, OutOfLevelError):
            return {
                p: self.level[p]
                for p in rect_space_at(rect.top_left.floor(), rect.bottom_right.floor())
            }
