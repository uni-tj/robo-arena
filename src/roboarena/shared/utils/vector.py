import math
import random
from dataclasses import dataclass
from typing import Callable, Sequence, TypeVar, Union, overload

import numpy as np
import pygame
from numpy.typing import NDArray
from pygame import Vector2


def sign(x: int | float) -> int:
    if x > 0:
        return 1
    if x < 1:
        return -1
    return 0


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

    def __str__(self) -> str:
        rx = self.round_to()
        return f"Vector(x={rx.x}, y={rx.y})"

    def to_tuple(self) -> tuple[T, T]:
        return (self.x, self.y)

    def to_pygame_vector2(self) -> pygame.Vector2:
        return pygame.Vector2(self.x, self.y)

    def to_np_array(self) -> NDArray[T]:
        return np.array([self.x, self.y])

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

    def round_to(self, n: int = 3) -> "Vector[float]":
        return self.apply_transform(lambda x: round(x, n))  # type:ignore

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector[float]":
        return self / self.length()

    def sign(self) -> "Vector[int]":
        return Vector(sign(self.x), sign(self.y))

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
    def dot[U: (int, float)](v1: "Vector[U]", v2: "Vector[U]") -> U:
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def angle_90(v1: "Vector[int | float]", v2: "Vector[int | float]") -> float:
        return math.acos(Vector.dot(v1, v2) / (v1.length() * v2.length()))

    @staticmethod
    def angle(v1: "Vector[int | float]", v2: "Vector[int | float]") -> float:
        """Returns the clockwise angle from v1 to v2 in [-pi, pi]"""
        dot = Vector.dot(v1, v2)
        det = v1.x * v2.y - v1.y * v2.x
        return math.atan2(det, dot)

    @staticmethod
    def zero() -> "Vector[float]":
        return Vector(0, 0)

    @staticmethod
    def one() -> "Vector[float]":
        return Vector(1, 1)

    @staticmethod
    def random() -> "Vector[float]":
        return Vector(random.random(), random.random())

    @staticmethod
    def random_unif(x: float, y: float) -> "Vector[float]":
        return Vector(random.uniform(x, y), random.uniform(x, y))

    @overload
    def sum_vectors(xs: list["Vector[int]"]) -> "Vector[int]": ...  # type:ignore
    @overload
    def sum_vectors(xs: list["Vector[float]"]) -> "Vector[float]": ...  # type:ignore

    @staticmethod
    def sum_vectors[K: (float, int)](xs: list["Vector[K]"]) -> "Vector[K]":
        res = Vector.zero()
        for x in xs:
            res += x.to_float()
        return res  # type:ignore


T = TypeVar("T", int, float)


class Matrix2d[K: (int, float)]:
    a11: K
    a12: K
    a21: K
    a22: K

    def __init__(self, a11: K, a12: K, a21: K, a22: K):
        self.a11 = a11
        self.a12 = a12
        self.a21 = a21
        self.a22 = a22

    @overload
    def __mul__(self, other: int) -> "Matrix2d[int]": ...  # type:ignore
    @overload
    def __mul__(self, other: float) -> "Matrix2d[float]": ...
    @overload
    def __mul__(self, other: Vector[int]) -> Vector[int]: ...
    @overload
    def __mul__(self, other: Vector[K]) -> Vector[K]: ...
    @overload
    def __mul__(self, other: "Matrix2d[int]") -> "Matrix2d[int]": ...
    @overload
    def __mul__(self, other: "Matrix2d[float]") -> "Matrix2d[float]": ...
    @overload
    def __mul__(self, other: "Matrix2d[K]") -> "Matrix2d[K]": ...

    def __mul__(  # type:ignore
        self, other: Union[int, float, Vector[T], "Matrix2d[T]"]
    ) -> Union["Matrix2d[int]", "Matrix2d[float]", Vector[int], Vector[float]]:
        if isinstance(other, (int, float)):
            return Matrix2d(
                self.a11 * other, self.a12 * other, self.a21 * other, self.a22 * other
            )
        elif isinstance(other, Vector):
            return Vector(
                self.a11 * other.x + self.a12 * other.y,
                self.a21 * other.x + self.a22 * other.y,
            )
        elif isinstance(other, Matrix2d):
            return Matrix2d(
                self.a11 * other.a11 + self.a12 * other.a21,
                self.a11 * other.a12 + self.a12 * other.a22,
                self.a21 * other.a11 + self.a22 * other.a21,
                self.a21 * other.a12 + self.a22 * other.a22,
            )
        else:
            raise TypeError("Unsupported operand type for *")

    @overload
    def __add__(self, other: "Matrix2d[T]") -> "Matrix2d[float]": ...
    @overload
    def __add__(self, other: "Matrix2d[K]") -> "Matrix2d[K]": ...  # type: ignore

    def __add__(  # type: ignore
        self, other: "Matrix2d[float]|Matrix2d[int]"
    ) -> "Matrix2d[float]|Matrix2d[int]":
        return Matrix2d(
            self.a11 + other.a11,
            self.a12 + other.a12,
            self.a21 + other.a21,
            self.a22 + other.a22,
        )

    @overload
    def __sub__(self, other: "Matrix2d[int]") -> "Matrix2d[float]": ...
    @overload
    def __sub__(self, other: "Matrix2d[float]") -> "Matrix2d[float]": ...

    def __sub__(self, other: "Matrix2d[T]") -> "Matrix2d[float]":
        return Matrix2d(
            self.a11 - other.a11,
            self.a12 - other.a12,
            self.a21 - other.a21,
            self.a22 - other.a22,
        )

    def transpose(self) -> "Matrix2d[K]":
        return Matrix2d(self.a11, self.a21, self.a12, self.a22)

    def determinant(self) -> K:
        return self.a11 * self.a22 - self.a12 * self.a21

    def inverse(self) -> "Matrix2d[float]":
        det = self.determinant()
        if det == 0:
            raise ValueError("Matrix is not invertible")
        inv_det = 1 / float(det)
        return Matrix2d(
            self.a22 * inv_det,
            -self.a12 * inv_det,
            -self.a21 * inv_det,
            self.a11 * inv_det,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix2d):
            return False
        return (  # type:ignore
            self.a11 == other.a11  # type:ignore
            and self.a12 == other.a12  # type:ignore
            and self.a21 == other.a21  # type:ignore
            and self.a22 == other.a22  # type: ignore
        )

    def __str__(self) -> str:
        return f"Matrix2d(\n  {self.a11}, {self.a12}\n  {self.a21}, {self.a22}\n)"

    @staticmethod
    def identity() -> "Matrix2d[int]":
        return Matrix2d(1, 0, 0, 1)

    @staticmethod
    def rot_matrix(alpha: float) -> "Matrix2d[float]":
        import math

        return Matrix2d(
            math.cos(alpha), -math.sin(alpha), math.sin(alpha), math.cos(alpha)
        )

    @staticmethod
    def scale_matrix(sx: float, sy: float) -> "Matrix2d[float]":
        return Matrix2d(sx, 0, 0, sy)

    @staticmethod
    def shear_matrix(shx: float, shy: float) -> "Matrix2d[float]":
        return Matrix2d(1, shx, shy, 1)
