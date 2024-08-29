from time import perf_counter

from attrs import define, field

type Time = float


def get_time() -> Time:
    return perf_counter()


def add_seconds(time: Time, add: Time) -> Time:
    return time + add


@define
class PreciseClock:
    min_dt: Time
    last_t: Time = field(factory=get_time, init=False)

    def tick(self) -> float:
        while get_time() - self.last_t < self.min_dt:
            pass
        t = get_time()
        dt = t - self.last_t
        self.last_t = t
        return dt
