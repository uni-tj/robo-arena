from roboarena.shared.utils.perf_tester import PerformanceTester

if __name__ == "__main__":

    def gen_data():
        return 10**3

    while_test = PerformanceTester(10_000, gen_data)

    def while_true(num: int):
        i = 0
        while True:
            i += 1
            if i <= num:
                continue
            break

    def while_1(num: int):
        i = 0
        while 1:
            i += 1
            if i <= num:
                continue
            break

    def while_data(num: int) -> int:
        return num

    while_test.add_function("while_true", while_true, while_data)
    while_test.add_function("while_1", while_1, while_data)

    while_test.compare_performance()
