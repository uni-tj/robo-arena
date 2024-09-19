import math
from typing import Optional

from roboarena.shared.utils.vector import Vector

type Point = tuple[float, float]
type Direction = tuple[float, float]
type Restriction = Optional[tuple[float, float]]
type Vc = Vector[float]


# class Line:
#     def __init__(
#         self,
#         origin: Vc,
#         direction: Vc,
#         restrict: Restriction = None,
#     ) -> None:
#         self.origin = origin.to_tuple()
#         self.direction = (direction).normalize().to_tuple()
#         self._restrict = restrict
#
#     @staticmethod
#     def _normalize(v: Direction) -> Direction:
#         length = math.sqrt(v[0] ** 2 + v[1] ** 2)
#         return (v[0] / length, v[1] / length)
#
#     @staticmethod
#     def from_angle(origin: Vc, angle: float, restrict: Restriction = None) -> "Line":
#         direction = Vector.from_angle(angle)
#         return Line(origin, direction, restrict)
#
#     @staticmethod
#     def from_points(a: Vc, b: Vc, restrict: Restriction = None) -> "Line":
#         direction = b - a
#         return Line(a, direction, restrict)
#
#     def check_restrict(self, t: float) -> bool:
#         if self._restrict is None:
#             return True
#         return self._restrict[0] <= t <= self._restrict[1]
#
#     def check_other_restrict(self, t: float, other: "Line") -> bool:
#         ix = self.origin[0] + self.direction[0] * t
#         iy = self.origin[1] + self.direction[1] * t
#         dx = ix - other.origin[0]
#         dy = iy - other.origin[1]
#         dot = dx * other.direction[0] + dy * other.direction[1]
#         return other.check_restrict(dot)
#
#     def is_on(self, p: Point) -> bool:
#         v = (p[0] - self.origin[0], p[1] - self.origin[1])
#         v_len = math.sqrt(v[0] ** 2 + v[1] ** 2)
#         cp = (
#             self.origin[0] + self.direction[0] * v_len,
#             self.origin[1] + self.direction[1] * v_len,
#         )
#         is_close = abs(cp[0] - p[0]) < 1e-6 and abs(cp[1] - p[1]) < 1e-6
#         dot = v[0] * self.direction[0] + v[1] * self.direction[1]
#         return is_close and self.check_restrict(dot)
#
#     def intersection(self, other: "Line") -> Optional[Vc]:
#         d, e = self.direction, other.direction
#         o, p = self.origin, other.origin
#         det = d[0] * e[1] - d[1] * e[0]
#         if abs(det) < 1e-6:
#             return None
#         t = (e[0] * (o[1] - p[1]) - e[1] * (o[0] - p[0])) / det
#         if not (self.check_restrict(t) and self.check_other_restrict(t, other)):
#             return None
#         return Vector(o[0] + d[0] * t, o[1] + d[1] * t)
#
#     def normal(self) -> Direction:
#         angle = math.atan2(self.direction[1], self.direction[0]) + math.pi / 2
#         return Vector(math.cos(angle), math.sin(angle))
#
#     def distance(self, point: Point) -> float:
#         proj = self.project(point)
#         dx = point[0] - proj[0]
#         dy = point[1] - proj[1]
#         return math.sqrt(dx**2 + dy**2)
#
#     def project(self, point: Point) -> Point:
#         v = (point[0] - self.origin[0], point[1] - self.origin[1])
#         t = v[0] * self.direction[0] + v[1] * self.direction[1]
#         return (
#             self.origin[0] + self.direction[0] * t,
#             self.origin[1] + self.direction[1] * t,
#         )
#
#     def render(self, rdr):
#         if self._restrict is None:
#             end = (
#                 self.origin[0] + self.direction[0],
#                 self.origin[1] + self.direction[1],
#             )
#             rdr(self.origin, end, (255, 255, 255))
#         else:
#             start = (
#                 self.origin[0] - self.direction[0] * self._restrict[0],
#                 self.origin[1] - self.direction[1] * self._restrict[0],
#             )
#             end = (
#                 self.origin[0] + self.direction[0] * self._restrict[1],
#                 self.origin[1] + self.direction[1] * self._restrict[1],
#             )
#             rdr(start, end)
#


class Line:
    origin: Point

    def __init__(
        self, origin: Point, direction: Direction, restrict: Restriction = None
    ) -> None:
        self.origin = origin
        self.direction = self._normalize(direction)
        self._restrict = restrict

    @staticmethod
    def from_vects(origin: Vc, direction: Vc, restrict: Restriction = None):
        return Line(origin.to_tuple(), direction.normalize().to_tuple(), restrict)

    @staticmethod
    def _normalize(v: Direction) -> Direction:
        length = math.sqrt(v[0] ** 2 + v[1] ** 2)
        return (v[0] / length, v[1] / length)

    @staticmethod
    def from_angle(origin: Point, angle: float, restrict: Restriction = None) -> "Line":
        direction = (math.cos(angle), math.sin(angle))
        return Line(origin, direction, restrict)

    @staticmethod
    def from_points(a: Point, b: Point, restrict: Restriction = None) -> "Line":
        direction = (b[0] - a[0], b[1] - a[1])
        return Line(a, direction, restrict)

    def check_restrict(self, t: float) -> bool:
        if self._restrict is None:
            return True
        return self._restrict[0] <= t <= self._restrict[1]

    def check_other_restrict(self, t: float, other: "Line") -> bool:
        ix = self.origin[0] + self.direction[0] * t
        iy = self.origin[1] + self.direction[1] * t
        dx = ix - other.origin[0]
        dy = iy - other.origin[1]
        dot = dx * other.direction[0] + dy * other.direction[1]
        return other.check_restrict(dot)

    def is_on(self, p: Point) -> bool:
        v = (p[0] - self.origin[0], p[1] - self.origin[1])
        v_len = math.sqrt(v[0] ** 2 + v[1] ** 2)
        cp = (
            self.origin[0] + self.direction[0] * v_len,
            self.origin[1] + self.direction[1] * v_len,
        )
        is_close = abs(cp[0] - p[0]) < 1e-6 and abs(cp[1] - p[1]) < 1e-6
        dot = v[0] * self.direction[0] + v[1] * self.direction[1]
        return is_close and self.check_restrict(dot)

    def intersection(self, other: "Line") -> Optional[Point]:
        d, e = self.direction, other.direction
        o, p = self.origin, other.origin
        det = d[0] * e[1] - d[1] * e[0]
        if abs(det) < 1e-6:
            return None
        t = (e[0] * (o[1] - p[1]) - e[1] * (o[0] - p[0])) / det
        if not (self.check_restrict(t) and self.check_other_restrict(t, other)):
            return None
        return (o[0] + d[0] * t, o[1] + d[1] * t)

    def normal(self) -> Direction:
        angle = math.atan2(self.direction[1], self.direction[0]) + math.pi / 2
        return (math.cos(angle), math.sin(angle))

    def distance(self, point: Point) -> float:
        proj = self.project(point)
        dx = point[0] - proj[0]
        dy = point[1] - proj[1]
        return math.sqrt(dx**2 + dy**2)

    def project(self, point: Point) -> Point:
        v = (point[0] - self.origin[0], point[1] - self.origin[1])
        t = v[0] * self.direction[0] + v[1] * self.direction[1]
        return (
            self.origin[0] + self.direction[0] * t,
            self.origin[1] + self.direction[1] * t,
        )

    def render(self, rdr):
        if self._restrict is None:
            end = (
                self.origin[0] + self.direction[0],
                self.origin[1] + self.direction[1],
            )
            rdr(self.origin, end, (255, 255, 255))
        else:
            start = (
                self.origin[0] - self.direction[0] * self._restrict[0],
                self.origin[1] - self.direction[1] * self._restrict[0],
            )
            end = (
                self.origin[0] + self.direction[0] * self._restrict[1],
                self.origin[1] + self.direction[1] * self._restrict[1],
            )
            rdr(start, end)
