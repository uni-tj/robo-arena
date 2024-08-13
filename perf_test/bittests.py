import random

from perf_tester import PerformanceTester

from roboarena.shared.util import (
    int2nd_arr,
    is_one_at,
    nd_arr2int,
    nonzero,
    nonzero_count,
    nonzero_inv,
    nonzerop,
    one_hot,
    ones,
    ones_except,
)


# generates all data any tested function could need
def gen_data() -> tuple[int, int, list[int]]:
    value = random.randint(0, 2**20 - 1)
    size = 32  # Adjust size as needed
    indices = [random.randint(0, 19) for _ in range(random.randint(1, 5))]
    return value, size, indices


if __name__ == "__main__":
    performance_tester = PerformanceTester(10_000_000, gen_data)

    # Adding all bitwise manipulation fuctions t othe test
    performance_tester.add_function(
        "nd_arr2int", nd_arr2int, lambda data: int2nd_arr(data[0], data[1])
    )
    performance_tester.add_function(
        "int2nd_arr", lambda x: int2nd_arr(x[0], x[1]), lambda data: (data[0], data[1])
    )
    performance_tester.add_function("nonzero_inv", nonzero_inv, lambda data: data[2])
    performance_tester.add_function("nonzero", nonzero, lambda data: data[0])
    performance_tester.add_function("nonzerop", nonzerop, lambda data: data[0])
    performance_tester.add_function(
        "nonzero_count", nonzero_count, lambda data: data[0]
    )
    performance_tester.add_function("ones", ones, lambda data: data[1])
    performance_tester.add_function(
        "one_hot", one_hot, lambda data: random.randint(0, data[1] - 1)
    )
    performance_tester.add_function(
        "ones_except",
        lambda x: ones_except(x[0], x[1]),
        lambda data: (data[1], random.randint(0, data[1] - 1)),
    )
    performance_tester.add_function(
        "is_one_at",
        lambda x: is_one_at(x[0], x[1]),
        lambda data: (data[0], random.randint(0, data[1] - 1)),
    )

    performance_tester.compare_performance()
