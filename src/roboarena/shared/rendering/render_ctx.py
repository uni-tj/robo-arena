import logging
from typing import TYPE_CHECKING

import pygame
from pygame import Surface

from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.types import FieldOfView

STANDARD_BLOCK_SIZE_PX = 50
STANDARD_GU_PER_SCREEN = 15
OVERLAP_FOV_GU = Vector(2.0, 2.0)


logger = logging.getLogger(f"{__name__}")


# @dataclass(frozen=True)
class RenderCtx:
    screen: Surface
    screen_dimenions_px: Vector[int]
    camera_position_gu: Vector[float]
    fov: "FieldOfView"
    px_per_gu: int
    scale_factor: float
    _scale_cache: dict[Surface, Surface]
    _logger = logging.getLogger(f"{__name__}.RenderCtx")

    def __init__(
        self,
        screen: Surface,
        camera_position_gu: Vector[float],
        scale_cache: dict[Surface, Surface],
    ):
        self.screen = screen
        self._scale_cache = scale_cache
        self.update_screen_dimensions()
        self.update_camera_position(camera_position_gu)

    def update_camera_position(self, camera_position_gu: Vector[float]):
        self.camera_position_gu = camera_position_gu
        self.fov = self.update_fov()
        logging.info(f"fov: {self.fov}")

    def update_screen_dimensions(self):
        self.screen_dimenions_px = Vector(
            self.screen.get_width(), self.screen.get_height()
        )
        self.update_scale()
        self._scale_cache = {}

    def update_fov(self) -> "FieldOfView":
        center_to_corner_distance_gu: Vector[float] = (
            self.screen_dimenions_px
            * Vector(1 / self.px_per_gu, 1 / self.px_per_gu)
            * Vector(0.5, 0.5)
        )
        fov_upper_left_corner_gu: Vector[int] = (
            self.camera_position_gu - center_to_corner_distance_gu
        ).ceil()
        fov_lower_right_corner_gu: Vector[int] = (
            self.camera_position_gu + center_to_corner_distance_gu
        ).floor()
        return (
            (fov_upper_left_corner_gu - OVERLAP_FOV_GU).ceil(),
            (fov_lower_right_corner_gu + OVERLAP_FOV_GU).ceil(),
        )

    def update_scale(self):
        self.px_per_gu = self.screen_dimenions_px.x // STANDARD_GU_PER_SCREEN
        self.scale_factor = self.px_per_gu / STANDARD_BLOCK_SIZE_PX

    def scale_texture(self, surface: Surface) -> Surface:
        cache_key = surface
        if cache_key not in self._scale_cache:
            self._logger.debug("texture cache miss")
            self._scale_cache[cache_key] = pygame.transform.scale_by(
                surface, self.scale_factor
            ).convert()
        return self._scale_cache[cache_key]

    def scale_value[T: (int, float)](self, value: T) -> T:
        return value * self.scale_factor  # type: ignore

    def scale_vector(self, vector: Vector[float]) -> Vector[float]:
        return vector * self.scale_factor

    def get_scale_cache(self) -> dict[Surface, Surface]:
        return self._scale_cache
