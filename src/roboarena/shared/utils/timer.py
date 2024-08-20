import time
from collections import defaultdict, deque
from math import nan
from typing import Optional

from roboarena.shared.utils.statistics import StatsCollection


class Timer:
    timings: dict[str, list[float]]
    last_started: deque[str]
    current: dict[str, float]
    stats_collection: StatsCollection

    def __init__(self):
        self.timings = defaultdict(list)
        self.last_started = deque()
        self.current = {}
        self.stats_collection = StatsCollection()
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

    def print_timings(self, label_to_group: Optional[dict[str, str]] = None) -> None:
        """Print the timing statistics for all labels,
        optionally assigning them to groups."""
        if label_to_group is None:
            label_to_group = {}

        # Create Stats objects for each label and store them in the stats_collection
        for label, times in self.timings.items():
            if not times:
                continue

            self.stats_collection.add_stats(
                label,
                times,
                group=label_to_group[label] if label in label_to_group else None,
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


if __name__ == "__main__":
    timer = Timer()

    timer.tick("operation_1")
    time.sleep(0.5)
    timer.tick_end("operation_1")

    for _ in range(10):
        timer.tick("operation_2")
        time.sleep(0.3)
        timer.tick_end("operation_2")

    timer.print_timings({"operation_1": "a"})
