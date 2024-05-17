from collections import deque
from time import perf_counter
from typing import (
    Callable,
    Optional,
)
import numpy as np

import pygame


class PerfClock:
    last_t = perf_counter()

    def tick(self, max_fps: float) -> float:
        min_dt = 1 / max_fps
        t = perf_counter()
        while t - self.last_t < min_dt:
            t = perf_counter()

        dt = t - self.last_t
        self.last_t = t
        return dt


class WrappedClock:
    clock = pygame.time.Clock()
    last_t = perf_counter()

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def tick(self, fps: float) -> float:
        self.clock.tick_busy_loop(fps)
        t = perf_counter()
        dt = t - self.last_t
        self.last_t = t
        return dt


def throttle(f: Callable[[], None], s: float):
    last_call: Optional[float] = None

    def throttled() -> None:
        nonlocal last_call
        this_call = perf_counter()
        if last_call is not None and (this_call - last_call) < s:
            return
        f()
        last_call = this_call

    return throttled


PIXELS_PER_UNIT = 50
FPS = 60
x = 5

pygame.init
flags = pygame.SCALED
display = pygame.display.set_mode((1000, 1000), flags=flags, vsync=1)
# clock = PerfClock()
clock = WrappedClock()
# clock = pygame.time.Clock()

# print_fps = throttle(lambda: print(f"fps: {clock.get_fps()}"), 0.2)


def _draw():
    display.fill("black")
    coords = (x * PIXELS_PER_UNIT, 5 * PIXELS_PER_UNIT)
    pygame.draw.circle(display, "green", coords, 1 * PIXELS_PER_UNIT)
    pygame.display.flip()


# draw = throttle(_draw, 1)
draw = _draw

last_t = perf_counter()

dts = deque[float]()


def _print_dts():
    global dts
    arr = np.array(dts)
    print(f"last dt: {dts[0]}")
    print(f"mean: {np.mean(arr)}")
    print(f"std : {np.std(arr)}")
    dts = []


print_dts = throttle(_print_dts, 3)

while True:
    # print_fps()

    # dt = float(clock.tick_busy_loop(FPS)) / 1000
    dt = clock.tick(FPS)
    dts.append(dt)
    # print_dts()
    # print(f"dt: {dt}")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        x += 5 * dt
    if keys[pygame.K_LEFT]:
        x -= 5 * dt

    pygame.event.pump()
    draw()
