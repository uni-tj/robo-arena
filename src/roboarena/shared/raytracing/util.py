import math
from typing import Optional

from roboarena.shared.utils.vector import Vector

type Restriction = Optional[tuple[float, float]]


class Line:
    origin: Vector[float]
    direction: Vector[float]
    _restrict: Restriction

    def __init__(
        self, origin: Vector[float], direction: Vector[float], restrict: Restriction
    ) -> None:
        self.origin = origin
        self.direction = direction.normalize()
        self._restrict = restrict

    @staticmethod
    def from_angle(
        origin: Vector[float], angle: float, restrict: Restriction
    ) -> "Line":
        return Line(origin, Vector.from_angle(angle), restrict)

    @staticmethod
    def from_points(
        a: Vector[float], b: Vector[float], restrict: Restriction
    ) -> "Line":
        return Line(a, b - a, restrict)

    def check_restrict(self, t: float) -> bool:
        if self._restrict is None:
            return True
        return self._restrict[0] <= t and t <= self._restrict[1]

    def check_other_restrict(self, t: float, other: "Line") -> bool:
        intersection = self.origin + self.direction * t

        return other.check_restrict(
            Vector.dot(intersection - other.origin, other.direction)
        )

    def is_on(self, p: Vector[float]) -> bool:
        v = p - self.origin
        cp = (self.direction * v.length()) + self.origin
        # return cp.is_close(p) # TODO check if the restriction is correct
        return cp.is_close(p) and self.check_restrict(
            Vector.dot(v, self.direction)
        )  # Check restriction based on distance along the line

    def intersection(self, other: "Line") -> Optional[Vector[float]]:
        d = self.direction
        e = other.direction
        o = self.origin
        p = other.origin

        det = d.x * e.y - d.y * e.x
        if det == 0:
            return None

        t = (e.x * (o.y - p.y) - e.y * (o.x - p.x)) / det
        return (
            o + d * t
            if self.check_restrict(t) and self.check_other_restrict(t, other)
            else None
        )

    def normal(self) -> Vector[float]:
        return Vector.from_angle(
            Vector.angle(self.direction, Vector(1, 0)) + math.pi / 2
        )

    def distance(self, point: Vector[float]) -> float:
        projection = self.project(point)

        return (point - projection).length()

    def project(self, point: Vector[float]) -> Vector[float]:
        v = point - self.origin

        t = Vector.dot(v, self.direction)

        return self.origin + self.direction * t

    def render(self, rdr):
        if self._restrict is None:
            rdr(self.origin, self.origin + self.direction, (255, 255, 255))
        rdr(
            self.origin - self.direction * self._restrict[0],
            self.origin + self.direction * self._restrict[1],
        )

    def blocks_along_ray(self) -> Iterable[Vector[int]]:
        t = 0
        while self.check_restrict(t):
            yield self.origin + self.direction * t
            t += 1
