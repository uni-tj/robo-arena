import time
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Callable, Optional

from roboarena.shared.utils.table_printer import print_table


class ProgressBarConfig:
    complete: str = "="
    incomplete: str = " "
    lbound: str = "["
    rbound: str = "]"
    seperator: str = "ǁ"


class ProgressBar:
    def __init__(
        self, total: int, bar_length: int = 50, pgc: Optional[ProgressBarConfig] = None
    ):
        self.total = total
        self.bar_length = bar_length
        self.step_size = max(1, total // bar_length)
        self.current_progress = 0
        self.start_time = time.time()
        if pgc is None:
            self._pgc = ProgressBarConfig()
        else:
            self._pgc: ProgressBarConfig = pgc

    def update(self, current: int):
        elapsed_time = time.time() - self.start_time
        progress = current / self.total
        block = int(round(self.bar_length * progress))

        if block > self.current_progress:
            self.current_progress = block
            eta = elapsed_time * (self.total / current - 1) if current > 0 else 0
            eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta))
            elapsed_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

            progress_display = (
                f"[{self._pgc.complete * block}{self._pgc.incomplete * (self.bar_length - block)}] "  # noqa: B950
                f"{current}/{self.total} ({progress * 100:.2f}%) {self._pgc.seperator} "
                f"Elapsed: {elapsed_formatted} {self._pgc.seperator} ETA: {eta_formatted}"  # noqa: B950
            )
            print(f"{progress_display}", end="\r")


def mean(data: list[float]):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError("mean requires at least one data point")
    return sum(data) / n  # in Python 2 use sum(data)/float(n)


def _ss(data: list[float]):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss


def stddev(data: list[float], ddof: int = 1):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError("variance requires at least two data points")
    ss = _ss(data)
    pvar = ss / (n - ddof)
    return pvar**0.5


# @dataclass
# class ExecutionStats:
#     stat_list: list["Stats"]
#     @property
#     def labels(self):
#         return ["avg", "std"]
#     def adjust_scale()


@dataclass(frozen=True)
class Stats:
    avg: float
    std: float
    _scale: float

    @staticmethod
    def from_res(res: list[float]) -> "Stats":
        avg = mean(res)
        std = stddev(res)
        _scale = 2
        return Stats(avg, std, _scale)

    @staticmethod
    def adjust_scale(value: float) -> tuple[float, str]:
        scales = [
            (1e-9, "ns"),
            (1e-6, "µs"),
            (1e-3, "ms"),
            (1, "s"),
        ]
        for factor, label in scales:
            if value < factor * 1e3:
                return value / factor, label
        return value, "s"

    def __str__(self) -> str:
        return f"avg: {self.avg:.6f} , std: {self.std:.6f}"

    def table_repr(self) -> list[str]:
        return [
            f"{self.avg*1000**self._scale:.6f}",
            f"{self.std*1000**self._scale:.6f}",
        ]


class PerformanceTester[A]:
    def __init__(self, num_tests: int, gen_data: Callable[[], A]):
        self.num_tests = num_tests
        self.functions: list[tuple[str, Callable[[A], Any], Callable[[Any], Any]]] = []
        self.generate_data: Callable[[], A] = gen_data
        self.results: dict[str, list[float]] = defaultdict(list)
        self.add_function("id", id, id)

    def add_function[
        T
    ](self, name: str, func: Callable[[T], Any], data_func: Callable[[A], T]):
        if not name:
            name = func.__name__
        self.functions.append((name, data_func, func))

    def run_tests(self):
        prog_bar = ProgressBar(self.num_tests)
        for i in range(self.num_tests):
            prog_bar.update(i)
            # print("update")
            data = self.generate_data()
            for name, data_func, func in self.functions:
                special_data = data_func(data)
                start_time = time.perf_counter()
                res = func(special_data)
                if isinstance(res, Iterable):
                    for _ in res:  # type: ignore
                        pass
                end_time = time.perf_counter()
                self.results[name].append(end_time - start_time)

    @staticmethod
    def run_test_mp[
        T, R
    ](func: Callable[[T], R], data_func: Callable[[A], T], data_block: list[A]) -> list[
        float
    ]:
        return []

    def compare_performance(self):
        self.run_tests()
        config = [["Function", "Average (ms)", "Std Dev (ms)"], ["__sep"]]

        for name, res in self.results.items():
            stats = Stats.from_res(res)
            config.append([name] + stats.table_repr())

        print_table(config)
