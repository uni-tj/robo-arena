import logging

from funcy import log_durations
from pygame import display

from roboarena.shared.block import Block, voidBlock
from roboarena.shared.entity import Entity
from roboarena.shared.rendering.render_ctx import RenderingCtx
from roboarena.shared.utils.vector import Vector

type Level = dict[Vector[int], Block]
type EntityId = int
type Entities = dict[EntityId, Entity]

logger = logging.getLogger(f"{__name__}")


class RenderEngine:

    @log_durations(logger.debug, "render_screen: ", "ms")
    def render_screen(
        self, ctx: RenderingCtx, level: Level, entities: Entities
    ) -> None:
        self.render_background(ctx, level)
        self.render_entities(ctx, entities)
        display.flip()

    # @log_durations(logger.debug, "render_background: ", "ms")
    def render_background(self, ctx: RenderingCtx, level: Level) -> None:
        ctx.screen.fill((0, 0, 0))
        for y in range(ctx.fov[0].y, ctx.fov[1].y):
            for x in range(ctx.fov[0].x, ctx.fov[1].x):
                block: Block | None = level.get(Vector(x, y))
                block_pos_px: Vector[float] = ctx.screen_dimenions_px * Vector(
                    0.5, 0.5
                ) - (ctx.camera_position_gu - Vector(x, y)) * Vector(
                    ctx.px_per_gu, ctx.px_per_gu
                )
                if block:
                    block.render_block(ctx, block_pos_px)
                else:
                    voidBlock.render_block(ctx, block_pos_px)

    # @log_durations(logger.debug, "render_entities: ", "ms")
    def render_entities(self, ctx: RenderingCtx, entities: Entities) -> None:
        for entity in entities.values():
            entity.render(ctx)
