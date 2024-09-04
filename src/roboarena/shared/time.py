from time import perf_counter
from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from roboarena.shared.types import Time


def get_time() -> "Time":
    """Abstract over the time module used."""
    return perf_counter()


def add_seconds(time: "Time", add: "Time") -> "Time":
    return time + add


@define
class PreciseClock:
    """
    A clock significantly more precise than pygame.Clock.

    Utilizes busy waiting.
    """

    min_dt: "Time"
    """The minimum frame length"""
    last_t: "Time" = field(factory=get_time, init=False)
    """The time the last frame started"""

    def tick(self) -> float:
        while get_time() - self.last_t < self.min_dt:
            pass
        t = get_time()
        dt = t - self.last_t
        self.last_t = t
        return dt
