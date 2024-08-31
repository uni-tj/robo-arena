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

    @cached_property
    def left(self) -> float:
        return self.top_left.x

    @cached_property
    def right(self) -> float:
        return self.top_left.x + self.width_height.x

    @cached_property
    def top(self) -> float:
        return self.top_left.y

    @cached_property
    def bottom(self) -> float:
        return self.top_left.y + self.width_height.y

    def contains(self, point: Vector[float]):
        x_ok = self.top_left.x <= point.x <= self.bottom_right.x
        y_ok = self.top_left.y <= point.y <= self.bottom_right.y
        return x_ok and y_ok

    def overlaps(self, rect: "Rect") -> bool:
        x_ok = self.left <= rect.right and self.right >= rect.left
        y_ok = self.top <= rect.bottom and self.bottom >= rect.top
        return x_ok and y_ok

    def expand(self, n: float) -> "Rect":
        """Expand the rectangle by n in each direction."""
        return Rect(self.top_left - n, self.width_height + 2 * n)

    def tramslate(self, translation: Vector[float]) -> "Rect":
        return Rect(self.top_left + translation, self.width_height)

    def centerAround(self, center: Vector[float]) -> "Rect":
        return Rect(center - self.width_height / 2, self.width_height)

    @staticmethod
    def from_top_left(top_left: Vector[float]):
        return Rect(top_left, Vector.zero())

    @staticmethod
    def from_width_height(width_height: Vector[float]):
        return Rect(Vector.zero(), width_height)

    @staticmethod
    def from_size(size: Vector[float]):
        return Rect(Vector.zero(), size)
