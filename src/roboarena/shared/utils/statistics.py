from collections import defaultdict
from math import nan
from typing import Callable, Optional

from roboarena.shared.utils.system_utils import cls
from roboarena.shared.utils.table_printer import print_table


def mean(data: list[float]):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        # raise ValueError("mean requires at least one data point")
        return nan
    return sum(data) / n


def _ss(data: list[float]):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss


def stddev(data: list[float], ddof: int = 1):
    """Calculates the standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        return nan
    ss = _ss(data)
    pvar = ss / (n - ddof)
    return pvar**0.5


class Stats:
    """Container for a sequence of data that computes statistics on the provided
    data, this includes automtic scaling and processing of units"""

    def __init__(
        self,
        data: list[float],
        functions: dict[str, Callable[[list[float]], float]],
        unitless: set[str],
    ):
        self._data = data
        self._metrics: dict[str, float] = {}
        self._scales: dict[str, str] = {}
        self._unitless: set[str] = unitless
        self._calculate_metrics(functions)

    def _calculate_metrics(
        self, functions: dict[str, Callable[[list[float]], float]]
    ) -> None:
        for label, func in functions.items():
            value = func(self._data)
            self._metrics[label] = value
            self._scales[label] = self._adjust_scale(value)
            if label in self._unitless:
                self._scales[label] = ""

    def _adjust_scale(self, value: float, unit: str = "s") -> str:
        """determines the appropriate scale for the given value"""
        scales = [
            (1e-9, "n" + unit),
            (1e-6, "µ" + unit),
            (1e-3, "m" + unit),
            (1, unit),
        ]
        for factor, label in scales:
            if abs(value) < factor * 1e2:
                return label
        return "s"

    def _scaled_metric(self, name: str, unit: str = "s") -> float:
        if name in self._unitless:
            return self._metrics[name]
        scale_label = self._scales[name]
        scale_factor = {
            "n" + unit: 1e9,
            "µ" + unit: 1e6,
            "m" + unit: 1e3,
            "s" + unit: 1,
        }[scale_label]
        return self._metrics[name] * scale_factor

    def __str__(self) -> str:
        metric_str = ", ".join(
            f"{name}: {self._scaled_metric(name):.2g} {self._scales[name]}"
            for name in self._metrics
        )
        return f"{metric_str}"

    def table_repr(self) -> list[str]:
        """generates the table row list for all metrics"""
        return [
            f"{self._scaled_metric(name):6.3f} {self._scales[name]}"
            for name in self._metrics
        ]


class StatsCollection:
    """Container for a collection of statistics. The data in each stat is
    evaluated using the registered metrics.
    Prints the result of the metric calculations using the    Table printer"""

    def __init__(self, default_metrics: bool = True):
        self._stats_constructors: dict[str, Callable[[list[float]], float]] = {}
        self._columns: list[str] = []
        self._stats: dict[str, Stats] = {}
        self._unitless: set[str] = set()
        if default_metrics:
            self.register_metrics(
                labels=["avg", "std", "min", "max"],
                functions=[mean, stddev, min, max],
                unitless=set(),
            )
        self.groups: dict[str, set[str]] = defaultdict(set)

    def clear(self):
        self._stats: dict[str, Stats] = {}
        self.groups: dict[str, set[str]] = defaultdict(set)

    def register_metrics(
        self,
        labels: list[str],
        functions: list[Callable[[list[float]], float]],
        unitless: Optional[set[str]],
    ) -> None:
        """registers a new metic for all newly added stats"""
        if unitless is not None:
            self._unitless = unitless
        else:
            self._unitless: set[str] = set()
        for label, func in zip(labels, functions):
            self._columns.append(label)
            self._stats_constructors[label] = func

    def add_stats(
        self, label: str, res: list[float], group: Optional[str] = None
    ) -> None:
        """adds a new stat to the collection"""
        stats = Stats(
            data=res, functions=self._stats_constructors, unitless=self._unitless
        )
        self._stats[label] = stats
        if group is not None:
            self.groups[group].add(label)
        else:
            self.groups["_"].add(label)

    def print_all_stats(self) -> None:
        """pretty prints the statistics table containing all metrics"""
        header = ["Label"] + self._columns
        config = [header, ["__sep"]]

        sorted_groups = sorted(self.groups.items(), key=lambda x: x[0])

        for group_name, labels in sorted_groups:
            for label in labels:
                stats = self._stats[label]
                row = [label] + stats.table_repr()
                config.append(row)

            # Add a separator between groups if there are more groups to print
            if group_name != sorted_groups[-1][0]:
                config.append(["__sep"])
        cls()  # Clear the Console for all types of systems
        print_table(config)


def example_usage():
    stats_collection = StatsCollection()

    stats_collection.register_metrics(
        labels=["avg", "std", "max", "min"],
        functions=[mean, stddev, max, min],
        unitless=set(),
    )

    results_1 = [0.001, 0.002, 0.0015]
    stats_collection.add_stats("test_1", results_1)

    results_2 = [0.003, 0.004, 0.0025]
    stats_collection.add_stats("test_2", results_2)

    stats_collection.print_all_stats()


if __name__ == "__main__":

    example_usage()
