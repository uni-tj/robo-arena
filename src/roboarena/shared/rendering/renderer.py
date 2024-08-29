import logging
import time
from abc import ABC
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import cache, cached_property
from math import ceil, floor, nan
from typing import TYPE_CHECKING

import numpy as np
import pygame
import pygame.freetype
from attrs import define, field
from pygame import Surface, display
from pygame.transform import smoothscale

from roboarena.shared.block import void
from roboarena.shared.constants import PX_PER_GU
from roboarena.shared.types import EntityId
from roboarena.shared.utils.rect import Rect
from roboarena.shared.utils.tuple_vector import (
    TupleVector,
    add_tuples,
    ceil_tuples,
    mul_tuples,
    round_tuples,
    sub_tuples,
    truediv_tuples,
)
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.client.client import GameState
    from roboarena.client.menu.menu import Menu

logger = logging.getLogger(f"{__name__}")


GU_PER_SCREEN = 25.0
FOV_OVERLAP_GU = 1.0

type FieldOfView = Rect
""" In game units """
type ScreenPosition = tuple[int, int]


@cache
def get_default_font() -> pygame.freetype.Font:
    pygame.freetype.init()
    return pygame.freetype.SysFont(None, 24)


@define
class FPSCounter:
    _frame_times: deque[float] = field(factory=lambda: deque(maxlen=101))
    _font = get_default_font()

    @property
    def fps_list(self) -> list[float]:
        return list(1 / np.array(np.diff(self._frame_times)))

    def tick(self):
        now = time.time()
        self._frame_times.append(now)

    def get_rolling_avg(self) -> float:
        if len(self._frame_times) < 2:
            return 0.0
        time_span = self._frame_times[-1] - self._frame_times[0]
        return (len(self._frame_times) - 1) / time_span if time_span > 0 else 0.0

    def get_95th_percentile(self) -> tuple[float, float]:
        if len(self._frame_times) < 2:
            return 0.0, 0.0
        sorted_frame_times = list(sorted(np.diff(self._frame_times)))
        enough_values = len(sorted_frame_times) == 100
        low_95 = 1 / sorted_frame_times[5] if enough_values else nan
        high_95 = 1 / sorted_frame_times[-5] if enough_values else nan
        return low_95, high_95

    def get_avg(self):
        if len(self._frame_times) < 2:
            return 0.0
        time_span = self._frame_times[-1] - self._frame_times[0]
        fps = (len(self._frame_times) - 1) / time_span if time_span > 0 else 0.0

        return fps

    def fps_text(self):
        rolling_avg = self.get_avg()
        high_95, low_95 = self.get_95th_percentile()
        return (
            f"Rolling FPS: {rolling_avg:.2f} | <5%: {low_95:.2f} | >95%: {high_95:.2f}"
        )

    def render(self, screen: pygame.Surface):
        fps_text = self.fps_text()
        img = self._font.render(fps_text, (255, 255, 255))[0]
        screen.blit(
            img,
            (
                screen.get_width() - 10 - img.get_width(),
                screen.get_height() - 10 - img.get_height(),
            ),
        )


@dataclass(frozen=True)
class GameRenderCtx:
    px_screen: Surface
    camera_position_gu: Vector[float]
    _logger = logging.getLogger(f"{__name__}.RenderCtx")

    @cached_property
    def screen_size_px(self) -> Vector[int]:
        return Vector.from_tuple(self.px_screen.get_size())

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
        return PX_PER_GU

    def gu2px(self, vector: Vector[float]) -> Vector[int]:
        return (vector * self.px_per_gu).round()

    def gu2px_tup(self, vector: TupleVector) -> TupleVector:
        return ceil_tuples(mul_tuples(vector, self.px_per_gu))

    def gu2screen(self, vector: Vector[float]) -> Vector[int]:
        return self.screen_center_px + self.gu2px(vector - self.camera_position_gu)  # type: ignore (subtracting two ints is int not float)

    def gu2screen_tup(self, vector: TupleVector) -> TupleVector:
        return add_tuples(
            self.screen_center_px.to_tuple(),
            self.gu2px_tup(sub_tuples(vector, self.camera_position_gu.to_tuple())),
        )

    def px2gu(self, vector_px: Vector[int]) -> Vector[float]:
        return vector_px / self.px_per_gu

    def screen2gu(self, vector: Vector[int]) -> Vector[float]:
        return self.px2gu(vector - self.screen_center_px) + self.camera_position_gu  # type: ignore (subtracting two ints is int not float)

    def pct2px(self, vector_pct: Vector[int]) -> Vector[float]:
        return self.screen_size_px * vector_pct / 100


@dataclass(frozen=True)
class MenuRenderCtx:
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
        return ceil(self.screen.get_width() / GU_PER_SCREEN)

    def gu2px(self, vector: Vector[float]) -> Vector[int]:
        return (vector * self.px_per_gu).ceil()

    def gu2px_tup(self, vector: TupleVector) -> TupleVector:
        return ceil_tuples(mul_tuples(vector, self.px_per_gu))

    def gu2screen(self, vector: Vector[float]) -> Vector[int]:
        ra = self.screen_center_px + self.gu2px(vector - self.camera_position_gu)  # type: ignore (subtracting two ints is int not float)

        return ra

    def gu2screen_tup(self, vector: TupleVector) -> TupleVector:
        return add_tuples(
            self.screen_center_px.to_tuple(),
            self.gu2px_tup(sub_tuples(vector, self.camera_position_gu.to_tuple())),
        )

    def scale_gu(self, surface: Surface, size: Vector[float]) -> Surface:
        cache_key = (surface, size)
        if cache_key not in self._scale_cache:
            self._logger.debug(f"texture cache miss: {cache_key}")
            self._scale_cache[cache_key] = pygame.transform.scale(
                surface, self.gu2px(size).to_tuple()
            ).convert_alpha()
        return self._scale_cache[cache_key]

    def px2gu(self, vector_px: Vector[int]) -> Vector[float]:
        return vector_px / self.px_per_gu

    def screen2gu(self, vector: Vector[int]) -> Vector[float]:
        return self.px2gu(vector - self.screen_center_px) + self.camera_position_gu  # type: ignore (subtracting two ints is int not float)

    def pct2px(self, vector_pct: Vector[int]) -> Vector[float]:
        return self.screen_size_px * vector_pct / 100


@define
class GameRenderer:
    _screen: Surface
    _game: "GameState"
    _fps_counter: FPSCounter = field(factory=FPSCounter)

    # ! TODO Debbuging only:
    _last_entity_pos: dict[EntityId, deque[Vector[float]]] = field(
        factory=lambda: defaultdict(lambda: deque(maxlen=60 * 10)), init=False
    )
    _last_camera_pos: deque[Vector[float]] = field(
        factory=lambda: deque(maxlen=60 * 10), init=False
    )

    def _gen_ctx(self, camera_position: Vector[float]) -> GameRenderCtx:
        screen_px = Surface(
            (Vector.one() * GU_PER_SCREEN * PX_PER_GU).to_tuple(), pygame.SRCALPHA
        )
        return GameRenderCtx(screen_px, camera_position)

    def _gen_menu_ctx(self, camera_position: Vector[float]) -> MenuRenderCtx:
        _scale_cache = {}
        return MenuRenderCtx(self._screen, camera_position, _scale_cache)

    def screen2gu(
        self, vector_px: Vector[int], camera_position: Vector[float]
    ) -> Vector[float]:
        return self._gen_ctx(camera_position).screen2gu(vector_px)

    def render(self, camera_position: Vector[float]) -> None:
        self._fps_counter.tick()

        ctx = self._gen_ctx(camera_position)
        mctx = self._gen_menu_ctx(camera_position)
        self._render_background(ctx)
        self._render_markers(ctx)
        self._render_entities(ctx)
        self._fps_counter.render(self._screen)
        self._render_game_ui(mctx)

        # ! Debugging only
        self._last_camera_pos.append(camera_position)
        self._render_debug_traces(ctx)

        scale_factor = max(
            self._screen.get_width() / ctx.px_screen.get_width(),
            self._screen.get_height() / ctx.px_screen.get_height(),
        )
        scaled_px_screen_size = mul_tuples(ctx.px_screen.get_size(), scale_factor)
        self._screen.blit(
            smoothscale(ctx.px_screen, scaled_px_screen_size),
            truediv_tuples(
                sub_tuples(scaled_px_screen_size, self._screen.get_size()), -2
            ),
        )
        display.flip()

    def _render_background(self, ctx: GameRenderCtx) -> None:
        self._screen.fill((0, 0, 0))
        for y in range(floor(ctx.fov.top_left.y), ceil(ctx.fov.bottom_right.y)):
            blit_sequence: list[tuple[Surface, ScreenPosition]] = list()
            for x in range(floor(ctx.fov.top_left.x), ceil(ctx.fov.bottom_right.x)):
                pos_gu = Vector(x, y)
                block = self._game.level.get(pos_gu) or void
                pos_screen = sub_tuples(
                    ctx.gu2screen_tup((x, y)),
                    (0, block.texture.get_height() - PX_PER_GU),
                )
                blit_sequence.append((block.texture, pos_screen))  # type: ignore
            ctx.px_screen.blits(blit_sequence)

    def _render_entities(self, ctx: GameRenderCtx) -> None:
        for eid, entity in self._game.entities.items():
            entity.render(ctx)
            self._last_entity_pos[eid].append(entity.position)

    def _render_game_ui(self, ctx: "MenuRenderCtx") -> None:
        self._game.game_ui.render(ctx)

    def _render_markers(self, ctx: GameRenderCtx) -> None:
        surface = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        for marker in self._game.markers:
            pygame.draw.circle(
                surface,
                marker.color.to_tuple(),
                ctx.gu2screen(marker.position).to_tuple(),
                5,
            )

    def _render_debug_traces(
        self,
        ctx: GameRenderCtx,
    ) -> None:
        surface = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        for ci, poss in enumerate(self._last_entity_pos.values()):
            for i, cpos in enumerate(poss):
                # if i % 10 != 0:
                # continue
                col = (255, 0, ci, floor(255 * (i / len(poss))))
                pygame.draw.circle(
                    surface,
                    col,
                    ctx.gu2screen(cpos).to_tuple(),
                    3,
                )
        for i, cpos in enumerate(self._last_camera_pos):
            # if i % 10 != 0:
            # continue
            col = (0, 0, 255, floor(255 * (i / len(self._last_camera_pos))))
            pygame.draw.circle(surface, col, ctx.gu2screen(cpos).to_tuple(), 3)
        self._screen.blit(surface, (0, 0))


class Renderer(ABC):
    _screen: Surface
    _game: "GameState"
    _fps_counter: FPSCounter
    _last_screen_size: Vector[int] | None
    _scale_cache: dict[tuple[Surface, Vector[float]], Surface]

    def __init__(self, screen: Surface) -> None:
        self._screen = screen
        self._last_screen_size = None
        self._scale_cache = {}
        self._fps_counter = FPSCounter()

    """ Helper functions
    """

    def _genCtx(self, camera_position: Vector[float]) -> MenuRenderCtx:
        screen_size = Vector.from_tuple(self._screen.get_size())
        if self._last_screen_size != screen_size:
            # reset scale cache
            self._last_screen_size = screen_size
            self._scale_cache = {}

        return MenuRenderCtx(self._screen, camera_position, self._scale_cache)

    def screen2gu(
        self, vector_px: Vector[int], camera_position: Vector[float]
    ) -> Vector[float]:
        return self._genCtx(camera_position).screen2gu(vector_px)


class MenuRenderer(Renderer):

    def __init__(self, screen: Surface) -> None:
        super().__init__(screen)

    def render(self, menu: "Menu") -> None:
        ctx = self._genCtx(Vector(0, 0))
        self._screen.blit(
            pygame.transform.scale(menu.background_texture, ctx.screen.get_size()),
            (0, 0),
        )
        for button in menu.buttons.values():
            button.render(ctx)
        for text_field in menu.text_fields.values():
            text_field.render(ctx)
        display.flip()
