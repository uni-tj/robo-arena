import logging
from typing import List

from funcy import log_durations

from roboarena.server.level_generation.level_config import UCM
from roboarena.server.level_generation.level_processing import tilesmap2levelmap
from roboarena.server.level_generation.wfc_new import (
    WFC,
    ConstraintMap,
    TileType,
    convUcmCm,
)

# from roboarena.shared.rendering.render_engine import RenderEngine
from roboarena.shared.types import Level
from roboarena.shared.util import dict_diff_keys, gen_coord_space
from roboarena.shared.utils.vector import Vector

logger = logging.getLogger(f"{__name__}")


class LevelGenerator:
    wfc: WFC
    constraint_map: ConstraintMap
    new_diff: bool
    last_level: Level
    tilesize: Vector[int]

    def __init__(self) -> None:
        self.ucm = UCM
        self.last_level: Level = {}
        self.new_diff: bool = True
        self.tilesize = Vector(5, 5)  # TODO needs to be changed
        self.constraint_map = convUcmCm(self.ucm)
        self.s = 3
        self._init_level()

    @log_durations(logger.critical, "init_level: ", "ms")
    def _init_level(self):
        s = 1
        self.wfc = WFC.init_wfc(s, s, list(TileType), self.constraint_map)
        self.wfc.collapse_map()

    def get_level(self) -> Level:
        tm = self.wfc.tiles
        new_level: Level = tilesmap2levelmap(tm, self.tilesize)
        if self.new_diff:
            self.last_level = new_level
            self.new_diff = False
            self.new_level = new_level
        return new_level

    def get_level_diff(self) -> Level:
        # return self.get_level()
        return dict_diff_keys(self.last_level, self.get_level())

    def extend_level(self, posm: List[Vector[float]]) -> Level:
        s = self.s
        extend_dir = gen_coord_space((-s, s), (-s, s))
        tposs = [
            (edir + (ppos // self.tilesize)).floor()
            for ppos in posm
            for edir in extend_dir
        ]
        if not self.wfc.extend_level(tposs):
            return {}
        self.wfc.collapse_map()
        self.new_diff = True
        diff = self.get_level_diff()
        return diff


if __name__ == "__main__":
    l_gen = LevelGenerator()

    ppos = Vector(2.5, 2.5)
    while True:
        ppos += Vector(1, 0)
        try:
            l_gen.extend_level([ppos])
        except Exception as e:
            logger.error(f"Error extending level: {e}")
        lvl = l_gen.get_level()
        print(l_gen.get_level_diff())
        input()

# if __name__ == "__main__":
#     l_gen = LevelGenerator()
#     pygame.init()
#     screen = pygame.display.set_mode((1000, 1000))
#     ppos = Vector(2.5, 2.5)
#     eng = RenderEngine(screen)
#     while True:
#         ppos += Vector(1, 0)
#         try:
#             l_gen.extend_level([ppos])
#         except Exception as e:
#             logger.error(f"Error extending level: {e}")
#         lvl = l_gen.get_level()
#         eng.render_screen(lvl, dict(), ppos)
#         print(l_gen.get_level_diff())
#         # time.sleep(1)
