from abc import ABC
from dataclasses import dataclass
from pygame import Surface, transform
from position import Vector
from render_ctx import RenderingCtx

STANDARD_BLOCK_SIZE_PX = 50


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface
    dimensions_px: Vector[int]

    def render_block(self, ctx: RenderingCtx, block_pos_px: Vector[float]) -> None:
        corrected_block_pos_px: tuple[float, float] = (
            block_pos_px
            + Vector(0, (STANDARD_BLOCK_SIZE_PX - self.dimensions_px.y) * ctx.scale)
        ).tuple_repr()
        ctx.screen.blit(
            transform.scale_by(self.texture, ctx.scale), corrected_block_pos_px
        )


class WallBlock(Block):
    pass


class FloorBlock(Block):
    pass


class VoidBlock(Block):
    pass


voidBlock = VoidBlock(Surface((50, 65)), Vector(50, 65))
voidBlock.texture.fill((0, 0, 0))
