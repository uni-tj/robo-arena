import logging
from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame import Surface

from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.render_ctx import RenderCtx

logger = logging.getLogger(f"{__name__}")
STANDARD_BLOCK_SIZE_PX = 50


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface
    dimensions_px: Vector[int]

    # @log_durations(logger.debug, "render_block: ", "ms")
    def render_block(self, ctx: "RenderCtx", block_pos_px: Vector[float]) -> None:
        corrected_block_pos_px: tuple[float, float] = (
            block_pos_px
            + ctx.scale_vector(Vector(0, STANDARD_BLOCK_SIZE_PX - self.dimensions_px.y))
        ).tuple_repr()
        ctx.screen.blit(ctx.scale_texture(self.texture), corrected_block_pos_px)


@dataclass(frozen=True)
class BlockCtx(ABC):
    graphics_path: Path
    collision: bool


class WallBlock(Block):
    pass


class FloorBlock(Block):
    pass


class VoidBlock(Block):
    pass


voidBlock = VoidBlock(Surface((50, 65)), Vector(50, 65))
voidBlock.texture.fill((0, 0, 0))
pygame.draw.circle(voidBlock.texture, "blue", (25, 32.5), 10)
