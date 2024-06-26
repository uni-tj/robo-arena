import math
from dataclasses import dataclass
from typing import Callable

from pygame import Vector2


@dataclass(frozen=True)
class Vector[T: (int, float)]:
    x: T
    y: T

    def __add__[
        S: (int, float, "Vector[int]", "Vector[float]")
    ](self, o: S) -> "Vector[float]":
        match o:
            case Vector(x, y):
                return Vector(self.x + x, self.y + y)
            case _:
                return Vector(self.x + o, self.y + o)

    def __sub__[
        S: (int, float, "Vector[int]", "Vector[float]")
    ](self, o: S) -> "Vector[float]":
        match o:
            case Vector(x, y):
                return Vector(self.x - x, self.y - y)
            case _:
                return Vector(self.x - o, self.y - o)

    def __mul__[S: (int, float)](self, o: "Vector[S]" | S) -> "Vector[float]":
        match o:
            case Vector(x, y):
                return Vector(self.x * x, self.y * y)
            case _:
                return Vector(self.x * o, self.y * o)

    def __truediv__[
        S: (int, float, "Vector[int]", "Vector[float]")
    ](self, o: S) -> "Vector[float]":
        match o:
            case Vector(x, y):
                return Vector(self.x / x, self.y / y)
            case _:
                return Vector(self.x / o, self.y / o)

    def __floordiv__[
        S: (int, float, "Vector[int]", "Vector[float]")
    ](self, o: S) -> "Vector[int]":
        return (self / o).floor()

    def apply_transform(self, f: Callable[[T], T] = lambda x: x):
        return Vector(f(self.x), f(self.y))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Vector):
            return False
        return (self.x - o.x, self.y - o.y) == (0, 0)  # type: ignore

    def to_tuple(self) -> tuple[T, T]:
        return (self.x, self.y)

    @staticmethod
    def from_tuple[U: (int, float)](tup: tuple[U, U]) -> "Vector[U]":
        return Vector(tup[0], tup[1])

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

    def round(self) -> "Vector[int]":
        return self.apply_transform(round)  # type: ignore

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector[float]":
        return self / self.length()

    def distance_to(self, to: "Vector[T]") -> float:
        return (to - self).length()  # type: ignore
