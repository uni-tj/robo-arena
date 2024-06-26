import logging
from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame import Surface

from roboarena.shared.rendering.util import size_from_texture
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.rendering.renderer import RenderCtx

logger = logging.getLogger(f"{__name__}")
STANDARD_BLOCK_SIZE_PX = 50


@dataclass(frozen=True)
class Block(ABC):
    texture: Surface

    @cached_property
    def texture_size(self) -> Vector[float]:
        """In game units"""
        return size_from_texture(self.texture, width=1.0)

    # @log_durations(logger.debug, "render: ", "ms")
    def render(self, pos_gu: Vector[float], ctx: "RenderCtx") -> None:
        scaled_texture = ctx.scale_gu(self.texture, self.texture_size)
        # the physical height of the block is simulated by larger y-size
        z_gu = self.texture_size.y - 1
        top_left_gu = pos_gu - Vector(0, z_gu)
        ctx.screen.blit(scaled_texture, ctx.gu2screen(top_left_gu).to_tuple())


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


voidTexture = Surface((50, 65))
voidTexture.fill((0, 0, 0))
pygame.draw.circle(voidTexture, "blue", (25, 40), 10)
voidBlock = VoidBlock(voidTexture)
