import time
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Callable, Optional

from roboarena.shared.utils.statistics import StatsCollection


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
            self._pgc = pgc

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


class PerformanceTester[A]:
    def __init__(self, num_tests: int, gen_data: Callable[[], A]):
        self.num_tests = num_tests
        self.functions: list[tuple[str, Callable[[A], Any], Callable[[Any], Any]]] = []
        self.generate_data: Callable[[], A] = gen_data
        self.results: dict[str, list[float]] = defaultdict(list)
        self.stats_collection = StatsCollection()

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

        # Create Stats objects for each function and store them in the stats_collection
        for name, res in self.results.items():
            self.stats_collection.add_stats(name, res)

        # Print all stats in the stats_collection
        self.stats_collection.print_all_stats()
