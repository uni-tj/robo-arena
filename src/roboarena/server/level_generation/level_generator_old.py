# from roboarena.server.level_generation.level_processing import Level
import logging
import time

import pygame
from funcy import log_durations

from roboarena.server.level_generation.level_config import UCM
from roboarena.server.level_generation.level_processing import tilesmap2levelmap
from roboarena.server.level_generation.wfc import (
    TileType,
    UserConstraintList,
    WfcCtx,
    generate_constraint_map,
    wave_function_collapse,
)
from roboarena.shared.rendering.render_engine import RenderEngine
from roboarena.shared.types import Level
from roboarena.shared.util import dict_diff_keys, gen_coord_space
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


class LevelGenerator:
    wfc_ctx: WfcCtx
    ConstraintMap: UserConstraintList
    new_diff: bool
    last_level: Level
    tilesize: Vector[int]

    def __init__(self) -> None:
        self.wfc_ctx = WfcCtx({}, {}, set())
        self.ucm = UCM
        self.last_level: Level = {}
        self.new_diff: bool = True
        self.tilesize = Vector(5, 5)  # TODO needs to be changed
        self.cm = generate_constraint_map(self.ucm)
        self._init_level()

    @log_durations(logger.critical, "init_level: ", "ms")
    def _init_level(self):
        self.wfc_ctx.init_square(1, 1)
        wave_function_collapse(self.wfc_ctx, self.cm)

    # @log_durations(logger.critical, "get_lvl: ", "ms")
    def get_level(self) -> Level:
        tm = self.wfc_ctx.nodes
        new_level: Level = tilesmap2levelmap(tm, self.tilesize)
        if self.new_diff:
            self.last_level = new_level
            self.new_diff = False
            self.new_level = new_level
        return new_level

    # @log_durations(logger.critical, "level_diff: ", "ms")
    def get_level_diff(self) -> Level:
        return dict_diff_keys(self.last_level, self.get_level())

    # @log_durations(logger.critical, "extend_lvl: ", "ms")
    def extend_level(self, posm: list[Vector[float]]) -> Level:
        s = 3
        extend_dir = gen_coord_space((-s, s), (-s, s))
        tposs = [
            (edir + (ppos // self.tilesize)).floor()
            for ppos in posm
            for edir in extend_dir
        ]
        update = self.wfc_ctx.add_nodes(
            tposs, set(x for x in TileType.__members__.values())
        )
        if not update:
            return {}
        # logger.critical(f"Extending level at: {posm}  \n{tposs}")
        t0 = time.time()
        wave_function_collapse(self.wfc_ctx, self.cm)
        logger.critical(f"Wfc_time {time.time() - t0}")
        self.new_diff = True
        diff = self.get_level_diff()
        return diff


if __name__ == "__main__":
    l_gen = LevelGenerator()
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    ppos = Vector(2.5, 2.5)
    eng = RenderEngine(screen)
    while True:
        ppos += Vector(1, 0)
        # try:
        #     l_gen.extend_level([ppos])
        # except:
        #     pass
        lvl = l_gen.get_level()
        eng.render_screen(lvl, dict(), ppos)
        # print(lvl)
        print(l_gen.get_level_diff())
        time.sleep(1)
