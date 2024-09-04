import math
import random
from multiprocessing import Pool
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from roboarena.shared.utils.perf_tester import PerformanceTester

TupleVector = Tuple[float, float]
TupleVectorInt = Tuple[int, int]


def random_gradient(ix: int, iy: int) -> TupleVector:
    # No precomputed gradients mean this works for any number of grid coordinates
    w: int = 32
    s: int = w // 2
    a: int = ix * 3284157443
    b: int = iy
    b ^= ((a << s) | (a >> (w - s))) & 0xFFFFFFFF
    b = (b * 1911520717) & 0xFFFFFFFF
    a ^= ((b << s) | (b >> (w - s))) & 0xFFFFFFFF
    a = (a * 2048419325) & 0xFFFFFFFF
    random: float = (a / 0xFFFFFFFF) * 2 * math.pi
    return (math.sin(random), math.cos(random))


def dot_grid_gradient(ix: int, iy: int, x: float, y: float) -> float:
    gradient: TupleVector = random_gradient(ix, iy)
    dx: float = x - float(ix)
    dy: float = y - float(iy)

    return dx * gradient[0] + dy * gradient[1]


def interpolate(a0: float, a1: float, w: float) -> float:
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0


def perlin(x: float, y: float) -> float:
    x0: int = int(x)
    y0: int = int(y)
    x1: int = x0 + 1
    y1: int = y0 + 1

    # compute interpolation
    sx: float = x - float(x0)
    sy: float = y - float(y0)

    n0: float = dot_grid_gradient(x0, y0, x, y)
    n1: float = dot_grid_gradient(x1, y0, x, y)
    ix0: float = interpolate(n0, n1, sx)
    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1: float = interpolate(n0, n1, sx)
    value: float = interpolate(ix0, ix1, sy)
    return value


def perline_noise_spot(
    part_coordx: float, part_coordy: float, num_octaves: int
) -> float:

    val: float = 0
    freq: float = 1
    amp: float = 1
    for _ in range(num_octaves):
        sample_x: float = part_coordx * freq
        sample_y: float = part_coordy * freq
        val += perlin(sample_x, sample_y) * amp
        freq *= 2
        amp /= 2
    # val *= 1.2
    # val = max(-1.0, min(1.0, val))
    return val


def perlin_noise(
    width: int, height: int, gridsize: int, num_octaves: int, center: TupleVector
) -> NDArray[np.double]:
    pixels = np.zeros((height, width), dtype=np.float32)
    center_x, center_y = center
    # progress = ProgressBar(width * height)
    for x in range(width):
        for y in range(height):
            # progress.step()
            sample_x: float = (x + center_x) / gridsize
            sample_y: float = (y + center_y) / gridsize
            val = perline_noise_spot(sample_x, sample_y, num_octaves)

            color: float = (val + 1.0) * 0.5
            pixels[y, x] = color

            pixels[y, x] = color
    return pixels


def perline_noise_spot_mp(
    args: tuple[int, int, float, float, int]
) -> tuple[int, int, float]:

    x, y, part_coordx, part_coordy, num_octaves = args
    val: float = 0
    freq: float = 1
    amp: float = 1
    for _ in range(num_octaves):
        sample_x: float = part_coordx * freq
        sample_y: float = part_coordy * freq
        val += perlin(sample_x, sample_y) * amp
        freq *= 2
        amp /= 2
    # val *= 1.2
    # val = max(-1.0, min(1.0, val))
    return x, y, val


def perlin_noise_mp(
    width: int, height: int, gridsize: int, num_octaves: int, center: TupleVector
) -> NDArray[np.double]:
    pixels = np.zeros((height, width), dtype=np.float32)
    center_x, center_y = center
    cargs = [
        (x, y, (x + center_x) / gridsize, (y + center_y) / gridsize, num_octaves)
        for x in range(width)
        for y in range(height)
    ]
    with Pool(10) as p:
        res = p.map(perline_noise_spot_mp, cargs)
        for x, y, val in res:
            pixels[y, x] = val
    return pixels


def perline_noise_spot_mp_inv(
    args: tuple[int, int, int, float, float, int]
) -> NDArray[np.double]:
    okt, w, h, cx, cy, gs = args
    pixels = np.zeros((h, w), dtype=np.float32)
    freq: float = 2**okt
    amp: float = 1 / (2**okt)
    c1 = freq / gs
    c1x = cx / c1
    c1y = cy / c1

    for x in range(w):
        for y in range(h):
            # progress.step()
            sample_x: float = x / c1 + c1x
            sample_y: float = y / c1 + c1y
            pixels[x, y] += perlin(sample_x, sample_y) * amp
    return pixels


def perlin_noise_mp_inv(
    width: int, height: int, gridsize: int, num_octaves: int, center: TupleVector
) -> NDArray[np.double]:
    pixels = np.zeros((height, width), dtype=np.float32)
    cargs = [
        (i, width, height, center[0], center[1], gridsize) for i in range(num_octaves)
    ]
    with Pool(10) as p:
        res = p.map(perline_noise_spot_mp_inv, cargs)
        for val in res:
            pixels += val
    colors = (pixels + 1.0) * 0.5
    return colors


def gen_data() -> tuple[int, int]:
    k = 100
    return random.randint(-k, k), random.randint(-k, k)


def id[T](x: T) -> T:
    return x


if __name__ == "__main__":
    print("")
    s = 1000
    fr = 10
    perf_tester = PerformanceTester(10, gen_data)
    perf_tester.add_function("perl", lambda x: perlin_noise(s, s, 20, fr, x), id)
    perf_tester.add_function("perl_mp", lambda x: perlin_noise_mp(s, s, 20, fr, x), id)
    perf_tester.add_function(
        "perl_mp_inv", lambda x: perlin_noise_mp_inv(s, s, 20, fr, x), id
    )
    perf_tester.compare_performance()
