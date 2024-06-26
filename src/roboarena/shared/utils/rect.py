from dataclasses import dataclass
from functools import cached_property

from roboarena.shared.utils.vector import Vector


@dataclass(frozen=True)
class Rect:
    """A class for rectangles over floats"""

    top_left: Vector[float]
    width_height: Vector[float]

    @cached_property
    def bottom_right(self) -> Vector[float]:
        return self.top_left + self.width_height

    def contains(self, point: Vector[float]):
        x_ok = self.top_left.x <= point.x <= self.bottom_right.x
        y_ok = self.top_left.y <= point.y <= self.bottom_right.y
        return x_ok and y_ok

    def expand(self, n: float) -> "Rect":
        """Expand the rectangle by n in each direction."""
        return Rect(self.top_left - n, self.width_height + 2 * n)
