from pygame import Surface
from position import Vector

# representing the upper left and lower right corners of the field of view
type FieldOfView = tuple[Vector[int], Vector[int]]

STANDARD_BLOCK_SIZE_PX = 50
STANDARD_GU_PER_SCREEN = 15
OVERLAP_FOV_GU = Vector(2, 2)


class RenderingCtx:
    screen: Surface
    screen_dimenions_px: Vector[int]
    camera_position_gu: Vector[float]
    fov: FieldOfView
    px_per_gu: int
    scale: float

    def __init__(self, screen: Surface):
        self.screen = screen
        self.update_screen_dimensions(Vector(screen.get_width(), screen.get_height()))
        self.update_camera_position(Vector(0, 0))

    def update_camera_position(self, camera_position_gu: Vector[float]):
        self.camera_position_gu = camera_position_gu
        self.fov = self.update_fov()

    def update_screen_dimensions(self, screen_dimensions_px: Vector[int]):
        self.screen_dimenions_px = screen_dimensions_px
        self.update_scale()

    def update_fov(self) -> FieldOfView:
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
        self.scale = self.px_per_gu / STANDARD_BLOCK_SIZE_PX
