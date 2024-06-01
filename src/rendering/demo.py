import pygame as py
from position import Vector
from render_engine import RenderEngine
from render_ctx import RenderingCtx
from block import Block, WallBlock, FloorBlock
from entity import Entity, Player
from math import sin, cos

type EntityId = int
type Entities = dict[EntityId, Entity]
type Level = dict[Vector[int], Block]

SCREEN_HEIGHT: int = 1000
SCREEN_WIDTH: int = 1900
STARTPOS_GU: Vector[float] = Vector(0, 0)
DIRECTIONS = {
    "Up": Vector(0, -0.25),
    "Down": Vector(0, 0.25),
    "Left": Vector(-0.25, 0),
    "Right": Vector(0.25, 0),
}
DIRECTION_CHANGE = {
    py.K_UP: DIRECTIONS["Up"],
    py.K_w: DIRECTIONS["Up"],
    py.K_DOWN: DIRECTIONS["Down"],
    py.K_s: DIRECTIONS["Down"],
    py.K_LEFT: DIRECTIONS["Left"],
    py.K_a: DIRECTIONS["Left"],
    py.K_RIGHT: DIRECTIONS["Right"],
    py.K_d: DIRECTIONS["Right"],
}

wallBlock = WallBlock(py.Surface((50, 65)), Vector(50, 65))
wallBlock.texture.fill((68, 71, 77))
front = py.Surface((50, 15))
front.fill((52, 53, 59))
wallBlock.texture.blit(front, (0, 50))

floorBlock = FloorBlock(py.Surface((50, 50)), Vector(50, 50))
floorBlock.texture.fill((192, 198, 209))
floorBlock2 = FloorBlock(py.Surface((50, 50)), Vector(50, 50))
floorBlock2.texture.fill((163, 169, 181))

player_Pos: Vector[float] = Vector(15, 15)
player = Player(py.Surface((15, 15)), Vector(15, 15), player_Pos)
player.texture.fill((138, 227, 153))
enemy_pos: float = 0
enemy = Player(
    py.Surface((15, 15)),
    Vector(15, 15),
    Vector(18 + sin(enemy_pos % 360), 18 + cos(enemy_pos % 360)),
)
enemy.texture.fill((209, 23, 63))

entities: Entities = {0: player, 1: enemy}
level: Level = {}

for a in range(7, 28):
    level[Vector(a, 10)] = wallBlock
    level[Vector(a, 22)] = wallBlock
for y in range(11, 22):
    level[Vector(7, y)] = wallBlock
    for x in range(8, 27):
        if y % 2 == 0:
            if x % 2 == 0:
                level[Vector(x, y)] = floorBlock
            else:
                level[Vector(x, y)] = floorBlock2
        else:
            if x % 2 == 0:
                level[Vector(x, y)] = floorBlock2
            else:
                level[Vector(x, y)] = floorBlock
    level[Vector(27, y)] = wallBlock

py.init()
screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=py.RESIZABLE)
py.display.set_caption("Render-Engine-Prototype")
ctx: RenderingCtx = RenderingCtx(screen)
ctx.update_camera_position(player_Pos)
re = RenderEngine()

while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            exit()
        if event.type == py.KEYDOWN and event.key in DIRECTION_CHANGE:
            player_Pos = player_Pos + DIRECTION_CHANGE[event.key]
            entities[0].position_gu = player_Pos
        if event.type == py.VIDEORESIZE:
            ctx.update_screen_dimensions(Vector(event.w, event.h))
    enemy_pos += 0.01
    entities[1].position_gu = Vector(
        18 + sin(enemy_pos % 360), 18 + cos(enemy_pos % 360)
    )
    ctx.update_camera_position(player_Pos)
    re.render_screen(ctx, level, entities)
    py.display.flip()
    py.time.delay(10)
