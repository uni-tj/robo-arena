import random
import time
from collections import defaultdict, deque
from math import nan
from typing import Optional

from roboarena.shared.utils.statistics import StatsCollection


class Timer:
    """Timer to measure the time taken to execute parts of code"""

    timings: dict[str, list[float]]
    last_started: deque[str]
    current: dict[str, float]
    stats_collection: StatsCollection
    _periodic_timing: Optional[int]
    _c: int
    _label_to_group: dict[str, str]

    def __init__(
        self,
        pereodic_printing: Optional[int] = None,
        label_to_group: Optional[dict[str, str]] = None,
        reset: bool = True,
    ):
        self.timings = defaultdict(list)
        self.last_started = deque()
        self.current = {}
        self.stats_collection = StatsCollection()
        self._periodic_timing = pereodic_printing
        self._c = 0
        self._label_to_group = label_to_group if label_to_group else {}
        self._reset = reset
        # The sum of all keys excluding "total"

        def relative_time(data: list[float]) -> float:
            sum_keys = set(self.timings.keys())
            sum_keys.discard("total")
            sum_keys.discard("Σ")
            total_sum = sum([sum(self.timings[key]) for key in sum_keys])

            if total_sum == 0:
                return nan
            return sum(data) / total_sum

        self.stats_collection.register_metrics(["%"], [relative_time], set("%"))
        self.stats_collection.register_metrics(["Σ"], [lambda x: sum(x)], set("%"))

    def tick(self, label: str) -> None:
        """Start timing for the given label."""
        self.last_started.append(label)
        self.current[label] = time.time()

    def tick_end(self, label: str | None = None) -> None:
        """End timing for the given label."""
        if label is None:
            label = self.last_started.pop()
        elif label not in self.current:
            raise ValueError(f"Label '{label}' was not started.")

        start_time = self.current.pop(label, None)
        if start_time is None:
            raise ValueError(f"No start time found for label '{label}'.")

        elapsed_time = time.time() - start_time
        self.timings[label].append(elapsed_time)

    def end_run(self) -> None:
        """Ends a run (used for periodic printing)."""
        self._c += 1
        while len(self.current) > 0:
            self.tick_end()
        if self._periodic_timing is None:
            return
        if self._c % self._periodic_timing == 0:
            self.print_timings()
            if self._reset:
                self.clear()

    def print_timings(self) -> None:
        """Print the timing statistics for all labels,
        optionally assigning them to groups."""

        # Create Stats objects for each label and store them in the stats_collection
        for label, times in self.timings.items():
            if not times:
                continue

            self.stats_collection.add_stats(
                label,
                times,
                group=(
                    self._label_to_group[label]
                    if label in self._label_to_group
                    else None
                ),
            )
        self.stats_collection.print_all_stats()

    def clear(self) -> None:
        """Clear all recorded timings."""
        self.timings.clear()
        self.last_started.clear()
        self.current.clear()
        self.stats_collection.clear()

    def reset_label(self, label: str) -> None:
        """Reset timings for a specific label."""
        if label in self.timings:
            del self.timings[label]
        if label in self.current:
            del self.current[label]
        if label in self.last_started:
            self.last_started.remove(label)


def test_func(timer: Timer):
    timer.tick("operation_1")
    for _ in range(10000):
        random.random()
    timer.tick_end("operation_1")
    for _ in range(10):
        timer.tick("operation_2")
        for _ in range(1000000):
            _ = random.random() * random.random()
        timer.tick_end("operation_2")
    timer.end_run()


if __name__ == "__main__":
    timer = Timer(10, {"operation_1": "a"}, False)
    for _ in range(100):
        test_func(timer)
        time.sleep(0.5)
