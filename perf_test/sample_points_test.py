import math
import random

from roboarena.shared.utils.perf_tester import PerformanceTester


def rejction_sampling_uniform(x):
    while True:
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x**2 + y**2 > 1:
            return x, y


def rejction_sampling_random(x):
    while True:
        x = random.random() * 2 - 1
        y = random.random() * 2 - 1
        if x**2 + y**2 > 1:
            return x, y


def circle_sample_uniform(x):
    a = random.random()
    r = random.uniform(-1, 1) * math.pi
    return a * math.cos(r), a * math.sin(r)


def circle_sample_random(x):
    a = random.random()
    r = random.random() * 2 * math.pi
    return a * math.cos(r), a * math.sin(r)


if __name__ == "__main__":

    def gen_data():
        pass

    def pass_func(x):
        pass

    perf_test = PerformanceTester(1_000_000, gen_data)
    perf_test.add_function("rej_unif", rejction_sampling_uniform, pass_func)
    perf_test.add_function("rej_random", rejction_sampling_random, pass_func)
    perf_test.add_function("circle_uniform", circle_sample_uniform, pass_func)
    perf_test.add_function("circle_random", circle_sample_random, pass_func)

    perf_test.compare_performance()
