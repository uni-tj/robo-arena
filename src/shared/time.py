from time import perf_counter

type Time = float


def get_time() -> Time:
    return perf_counter()


def add_seconds(time: Time, add: Time) -> Time:
    return time + add
