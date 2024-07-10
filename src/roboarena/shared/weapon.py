from abc import ABC

from pygame import Surface

from roboarena.shared.util import load_graphic

LASER_GUN_TEXTURE = load_graphic("weapons/laser-gun.png")


class Weapon(ABC):

    texture: Surface
    damage: float


class LaserGun(Weapon):

    texture: Surface = LASER_GUN_TEXTURE
    damage: float = 10.0
