import math
from dataclasses import dataclass
from typing import Callable, Sequence, overload

from pygame import Vector2


@dataclass(frozen=True)
class Vector[T: (int, float)]:
    x: T
    y: T

    @overload
    def __add__(self, o: T) -> "Vector[T]": ...  # type: ignore

    @overload
    def __add__(self, o: "Vector[T]") -> "Vector[T]": ...

    @overload
    def __add__(
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float]": ...

    def __add__(  # type: ignore
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float] | Vector[int]":
        match o:
            case Vector(x, y):
                return Vector(self.x + x, self.y + y)
            case _:
                return Vector(self.x + o, self.y + o)

    @overload
    def __sub__(self, o: T) -> "Vector[T]": ...  # type: ignore

    @overload
    def __sub__(self, o: "Vector[T]") -> "Vector[T]": ...

    @overload
    def __sub__(
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float]": ...

    def __sub__(  # type: ignore
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float] | Vector[int]":
        match o:
            case Vector(x, y):
                return Vector(self.x - x, self.y - y)
            case _:
                return Vector(self.x - o, self.y - o)

    @overload
    def __mul__(self, o: T) -> "Vector[T]": ...  # type: ignore

    @overload
    def __mul__(self, o: "Vector[T]") -> "Vector[T]": ...

    @overload
    def __mul__(
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float]": ...

    def __mul__(  # type: ignore
        self, o: "int | float | Vector[int] | Vector[float]"
    ) -> "Vector[float] | Vector[int]":
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

    @staticmethod
    def from_sequence[U: (int, float)](x: Sequence[U]) -> "Vector[U]":
        return Vector(x[0], x[1])

    @staticmethod
    def from_scalar[U: (int, float)](x: U) -> "Vector[U]":
        return Vector(x, x)

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

    def any_leq(self, o: "Vector[T]") -> bool:
        return self.x <= o.x or self.y <= o.y

    def any_geq(self, o: "Vector[T]") -> bool:
        return self.x >= o.x or self.y >= o.y

    def mirror(self) -> "Vector[T]":
        return Vector(self.y, self.x)

    def to_float(self) -> "Vector[float]":
        return Vector(float(self.x), float(self.y))

    def to_int(self) -> "Vector[int]":
        return Vector(int(self.x), int(self.y))

    @staticmethod
    def zero() -> "Vector[float]":
        return Vector(0, 0)

    @staticmethod
    def one() -> "Vector[float]":
        return Vector(1, 1)
