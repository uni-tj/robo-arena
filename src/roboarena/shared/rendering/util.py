from pygame import Surface

from roboarena.shared.utils.vector import Vector


def size_from_texture(texture: Surface, *, width: float) -> Vector[float]:
    """Derive texture size in gu by specifying only width"""
    texture_size_px = Vector.from_tuple(texture.get_size())
    return texture_size_px / texture_size_px.x * width
