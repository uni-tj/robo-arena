import logging

from pygame import Surface, display

from roboarena.shared.block import Block, voidBlock
from roboarena.shared.rendering.render_ctx import RenderCtx
from roboarena.shared.types import Entities, Level
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")

logger = logging.getLogger(f"{__name__}")


class RenderEngine:

    ctx: RenderCtx

    def __init__(self, screen: Surface) -> None:
        self.ctx = RenderCtx(screen, Vector(0, 0), {})

    def screen2gu_vector(self, vector_px: Vector[int]) -> Vector[float]:
        return self.ctx.screen2gu_vector(vector_px)

    # @log_durations(logger.debug, "render_screen: ", "ms")
    def render_screen(
        self, level: Level, entities: Entities, player_pos_gu: Vector[float]
    ) -> None:
        self.update_ctx(player_pos_gu)
        self.render_background(level)
        self.render_entities(entities)
        display.flip()

    # @log_durations(logger.debug, "render_background: ", "ms")
    def render_background(self, level: Level) -> None:
        self.ctx.screen.fill((0, 0, 0))
        for y in range(self.ctx.fov[0].y, self.ctx.fov[1].y):
            for x in range(self.ctx.fov[0].x, self.ctx.fov[1].x):
                block: Block | None = level.get(Vector(x, y))
                block_pos_px: Vector[float] = self.ctx.screen_dimenions_px * Vector(
                    0.5, 0.5
                ) - (self.ctx.camera_position_gu - Vector(x, y)) * Vector(
                    self.ctx.px_per_gu, self.ctx.px_per_gu
                )
                if block:
                    block.render_block(self.ctx, block_pos_px)
                else:
                    voidBlock.render_block(self.ctx, block_pos_px)

    # @log_durations(logger.debug, "render_entities: ", "ms")
    def render_entities(self, entities: Entities) -> None:
        for entity in entities.values():
            entity.render(self.ctx)

    def update_ctx(self, player_pos_gu: Vector[float]) -> None:
        self.ctx = RenderCtx(self.ctx.screen, player_pos_gu, self.ctx.get_scale_cache())
