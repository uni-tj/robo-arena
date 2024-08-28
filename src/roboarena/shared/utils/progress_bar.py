import time
from typing import Optional


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
        self._c = 0
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

    def step(self):
        self._c += 1
        self.update(self._c)
