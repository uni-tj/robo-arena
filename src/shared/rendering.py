from pygame import Vector2

PIXELS_PER_BLOCK = 20


def px[T: int | Vector2 | float](unit: T) -> T:
    """Calculate px from game units"""
    match unit:
        case Vector2():
            return unit * PIXELS_PER_BLOCK
        case int():
            return unit * PIXELS_PER_BLOCK  # type: ignore
        case float():
            return unit * PIXELS_PER_BLOCK  # type: ignore
