from dataclasses import dataclass
from functools import cached_property

from roboarena.shared.utils.rect import Rect as VectorRect
from roboarena.shared.utils.tuple_vector import add_tuples, sub_tuples

type TupleVector = tuple[float, float]


@dataclass(frozen=True)
class Rect:
    """A class for rectangles over floats"""

    top_left: TupleVector
    width_height: TupleVector

    @staticmethod
    def from_vect_rect(rec: VectorRect) -> "Rect":
        return Rect(rec.top_left.to_tuple(), rec.width_height.to_tuple())

    @cached_property
    def bottom_right(self) -> TupleVector:
        return add_tuples(self.top_left, self.width_height[0])

    @cached_property
    def left(self) -> float:
        return self.top_left[0]

    @cached_property
    def right(self) -> float:
        return self.top_left[0] + self.width_height[0]

    @cached_property
    def top(self) -> float:
        return self.top_left[1]

    @cached_property
    def bottom(self) -> float:
        return self.top_left[1] + self.width_height[1]

    def contains(self, point: TupleVector):
        x_ok = self.top_left[0] <= point[0] <= self.bottom_right[0]
        y_ok = self.top_left[1] <= point[1] <= self.bottom_right[1]
        return x_ok and y_ok

    def overlaps(self, rect: "Rect") -> bool:
        x_ok = self.left <= rect.right and self.right >= rect.left
        y_ok = self.top <= rect.bottom and self.bottom >= rect.top
        return x_ok and y_ok

    @cached_property
    def half_diag(self):
        v = sub_tuples(self.bottom_right, self.top_left)
        return (v[0] ** 2 + v[1] ** 2) ** (0.5) / 2
