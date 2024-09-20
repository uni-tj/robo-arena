import math
from functools import cache
from typing import Iterable, Optional, Tuple

from line_module import Line as CppLine

# Type aliases for clarity
type Point = Tuple[float, float]
type Direction = Tuple[float, float]
type Restriction = Optional[Tuple[float, float]]


class Line:
    def __init__(
        self, origin: Point, direction: Direction, restrict: Restriction = None
    ) -> None:
        # Initialize the C++ Line object
        self._cpp_line: CppLine = CppLine(origin, direction, restrict)
        self.origin = origin
        self.direction = self._cpp_line.direction
        self._restrict = restrict

    def g(self, t: float) -> Point:
        # Delegate to the C++ method
        return self._cpp_line.g(t)

    @cache
    def h(self, x: float) -> float:
        # Delegate to the C++ method and cache the result
        return self._cpp_line.h(x)

    @staticmethod
    def from_angle(origin: Point, angle: float, restrict: Restriction = None) -> "Line":
        # Create a Line using the C++ static method
        cpp_line = CppLine.from_angle(origin, angle, restrict)
        # Wrap it in the Python Line class
        line = Line.__new__(Line)
        line._cpp_line = cpp_line
        line.origin = origin
        line.direction = cpp_line.direction
        line._restrict = restrict
        return line

    @staticmethod
    def from_points(a: Point, b: Point, restrict: Restriction = None) -> "Line":
        cpp_line = CppLine.from_points(a, b, restrict)
        line = Line.__new__(Line)
        line._cpp_line = cpp_line
        line.origin = a
        line.direction = cpp_line.direction
        line._restrict = restrict
        return line

    def check_restrict(self, t: float) -> bool:
        return self._cpp_line.check_restrict(t)

    def check_other_restrict(self, t: float, other: "Line") -> bool:
        return self._cpp_line.check_other_restrict(t, other._cpp_line)

    def is_on(self, p: Point) -> bool:
        return self._cpp_line.is_on(p)

    def intersection(self, other: "Line") -> Optional[Point]:
        result = self._cpp_line.intersection(other._cpp_line)
        return result if result is not None else None

    def normal(self) -> Direction:
        return self._cpp_line.normal()

    def distance(self, point: Point) -> float:
        return self._cpp_line.distance(point)

    def project(self, point: Point) -> Point:
        return self._cpp_line.project(point)

    def blocks_along_line(self) -> Iterable[Tuple[int, int]]:
        # The C++ method returns a list; we can return an iterator if needed
        return iter(self._cpp_line.blocks_along_line())

    def render(self, rdr):
        # Implement render method in Python since it's not in the C++ class
        if self._restrict is None:
            end = (
                self.origin[0] + self.direction[0],
                self.origin[1] + self.direction[1],
            )
            rdr(self.origin, end, (255, 255, 255))
        else:
            start = (
                self.origin[0] + self.direction[0] * self._restrict[0],
                self.origin[1] + self.direction[1] * self._restrict[0],
            )
            end = (
                self.origin[0] + self.direction[0] * self._restrict[1],
                self.origin[1] + self.direction[1] * self._restrict[1],
            )
            rdr(start, end)

    @staticmethod
    def _normalize(v: Direction) -> Direction:
        # Optional: If needed, replicate normalization in Python
        length = math.hypot(v[0], v[1])
        return (v[0] / length, v[1] / length)

    @staticmethod
    def from_vects(origin, direction, restrict: Restriction = None):
        # Assuming 'Vector' class is available in your project
        return Line(origin.to_tuple(), direction.normalize().to_tuple(), restrict)
