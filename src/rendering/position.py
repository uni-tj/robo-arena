import math
from dataclasses import dataclass
from typing import Callable

from pygame import Vector2


@dataclass(frozen=True)
class Vector[T: (int, float)]:
    x: T
    y: T

    def __add__[
        S: (int, float)
    ](self, o: "Vector[S]",) -> "Vector[float]":
        return Vector(self.x + o.x, self.y + o.y)

    def __mul__[
        S: (int, float)
    ](self, o: "Vector[S]",) -> "Vector[float]":
        return Vector(self.x * o.x, self.y * o.y)

    def __sub__[
        S: (int, float)
    ](self, o: "Vector[S]",) -> "Vector[float]":
        return Vector(self.x - o.x, self.y - o.y)

    def apply_transform(self, f: Callable[[T], T] = lambda x: x):
        return Vector(f(self.x), f(self.y))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Vector):
            return False
        return (self.x - o.x, self.y - o.y) == (0, 0)  # type: ignore

    def tuple_repr(self) -> tuple[T, T]:
        return (self.x, self.y)

    def vector2_repr(self) -> Vector2:
        return Vector2(self.x, self.y)

    def drawing_coords(self, size: T) -> tuple[T, T, T, T]:
        return self.x * size, self.y * size, size, size

    def dot_product(self, o: "Vector[T]") -> T:
        return self.x * o.x + self.y * o.y

    def ceil(self) -> "Vector[int]":
        return self.apply_transform(math.ceil)  # type: ignore

    def floor(self) -> "Vector[int]":
        return self.apply_transform(math.floor)  # type: ignore
