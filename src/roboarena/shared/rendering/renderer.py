import logging
from dataclasses import dataclass
from functools import cached_property
from math import ceil, floor
from typing import TYPE_CHECKING

import pygame
from pygame import Surface, display

from roboarena.shared.block import voidBlock
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import GameState

logger = logging.getLogger(f"{__name__}")


GU_PER_SCREEN = 15.0
FOV_OVERLAP_GU = 1.0

type FieldOfView = Rect
""" In game units """


@dataclass(frozen=True)
class RenderCtx:
    screen: Surface
    camera_position_gu: Vector[float]
    _scale_cache: dict[tuple[Surface, Vector[float]], Surface]
    _logger = logging.getLogger(f"{__name__}.RenderCtx")

    @cached_property
    def screen_size_px(self) -> Vector[int]:
        return Vector.from_tuple(self.screen.get_size())

    @cached_property
    def screen_center_px(self) -> Vector[int]:
        return self.screen_size_px // 2

    @cached_property
    def fov(self) -> FieldOfView:
        top_left = self.screen2gu(Vector(0, 0))
        width_height = self.px2gu(self.screen_size_px)
        return Rect(top_left, width_height).expand(FOV_OVERLAP_GU)

    """ Conversion functions
    """

    @cached_property
    def px_per_gu(self) -> float:
        return self.screen.get_width() / GU_PER_SCREEN

    def gu2px(self, vector: Vector[float]) -> Vector[int]:
        return (vector * self.px_per_gu).floor()

    def gu2screen(self, vector: Vector[float]) -> Vector[int]:
        return self.screen_center_px + self.gu2px(vector - self.camera_position_gu)  # type: ignore (subtracting two ints is int not float)

    def scale_gu(self, surface: Surface, size: Vector[float]) -> Surface:
        cache_key = (surface, size)
        if cache_key not in self._scale_cache:
            self._logger.debug(f"texture cache miss: {cache_key}")
            self._scale_cache[cache_key] = pygame.transform.scale(
                surface, self.gu2px(size).to_tuple()
            ).convert()
        return self._scale_cache[cache_key]

    def px2gu(self, vector_px: Vector[int]) -> Vector[float]:
        return vector_px / self.px_per_gu

    def screen2gu(self, vector: Vector[int]) -> Vector[float]:
        return self.px2gu(vector - self.screen_center_px) + self.camera_position_gu  # type: ignore (subtracting two ints is int not float)


class Renderer:
    _screen: Surface
    _game: "GameState"

    _last_screen_size: Vector[int] | None
    _scale_cache: dict[tuple[Surface, Vector[float]], Surface]

    def __init__(self, screen: Surface, game: "GameState") -> None:
        self._screen = screen
        self._game = game
        self._last_screen_size = None
        self._scale_cache = {}

    """ Helper functions
    """

    def _genCtx(self, camera_position: Vector[float]) -> RenderCtx:
        return RenderCtx(self._screen, camera_position, self._scale_cache)

    def screen2gu(
        self, vector_px: Vector[int], camera_position: Vector[float]
    ) -> Vector[float]:
        return self._genCtx(camera_position).screen2gu(vector_px)

    """ Rendering functions
    """

    # @log_durations(logger.debug, "render: ", "ms")
    def render(self, camera_position: Vector[float]) -> None:
        screen_size = Vector.from_tuple(self._screen.get_size())
        if self._last_screen_size != screen_size:
            # reset scale cache
            self._last_screen_size = screen_size
            self._scale_cache = {}

        ctx = self._genCtx(camera_position)
        self._render_background(ctx)
        self._render_entities(ctx)
        display.flip()

    # @log_durations(logger.debug, "_render_background: ", "ms")
    def _render_background(self, ctx: RenderCtx) -> None:
        self._screen.fill((0, 0, 0))
        for y in range(floor(ctx.fov.top_left.y), ceil(ctx.fov.bottom_right.y)):
            for x in range(floor(ctx.fov.top_left.x), ceil(ctx.fov.bottom_right.x)):
                pos_gu = Vector(x, y)
                block = self._game.level.get(pos_gu) or voidBlock
                block.render(pos_gu * 1.0, ctx)

    # @log_durations(logger.debug, "_render_entities: ", "ms")
    def _render_entities(self, ctx: RenderCtx) -> None:
        for entity in self._game.entities.values():
            entity.render(ctx)
