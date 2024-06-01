from abc import ABC
from pygame import Surface, transform
from position import Vector
from render_ctx import RenderingCtx

# representing the upper left and lower right corners of the field of view
type FieldOfView = tuple[Vector[int], Vector[int]]


class Entity(ABC):
    texture: Surface
    dimensions_px: Vector[int]
    position_gu: Vector[float]

    def __init__(
        self, texture: Surface, dimensions_px: Vector[int], position_gu: Vector[float]
    ):
        self.texture = texture
        self.dimensions_px = dimensions_px
        self.position_gu = position_gu

    def visible_in_fov(self, fov: FieldOfView) -> bool:
        return (
            self.position_gu.x >= fov[0].x
            and self.position_gu.x <= fov[1].x
            and self.position_gu.y >= fov[0].y
            and self.position_gu.y <= fov[1].y
        )

    def render(self, ctx: RenderingCtx) -> None:
        if not self.visible_in_fov(ctx.fov):
            return
        entity_pos_px: Vector[float] = ctx.screen_dimenions_px * Vector(0.5, 0.5) - (
            ctx.camera_position_gu - self.position_gu
        ) * Vector(ctx.px_per_gu, ctx.px_per_gu)
        corrected_entity_pos_px: tuple[float, float] = (
            entity_pos_px
            - self.dimensions_px * Vector(0.5, 0.5) * Vector(ctx.scale, ctx.scale)
        ).tuple_repr()
        ctx.screen.blit(
            transform.scale_by(self.texture, ctx.scale), corrected_entity_pos_px
        )

    def update_position(self, new_position: Vector[float]) -> None:
        self.position_gu = new_position


class Player(Entity):
    pass


class Enemy(Entity):
    pass
