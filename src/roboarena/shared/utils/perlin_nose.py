import math
import random
from multiprocessing import Pool
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from roboarena.shared.utils.perf_tester import PerformanceTester
from roboarena.shared.utils.vector import Vector

TupleVector = Tuple[float, float]
TupleVectorInt = Tuple[int, int]


def random_gradient(ix: int, iy: int) -> TupleVector:
    """Function to generate a random gradient, the function is pure"""
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
    # qubic interpolation of two values
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0


def perlin(x: float, y: float) -> float:
    """Generates perlin noise for one positions"""
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


def perline_noise_spot_patial(
    part_coordx: float, part_coordy: float, num_octaves: int
) -> float:
    """Calulate the stacked perlin noise for one spot based on partial coordinate"""
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
    val = max(-1.0, min(1.0, val))
    return val


def perlin_noise_spot(pos: Vector[int], gridsize: int, num_octaves: int):
    """Generate perlin noise value for a spot based on coordinates"""
    return (
        perline_noise_spot_patial(pos.x / gridsize, pos.y / gridsize, num_octaves) + 1
    ) * 0.5


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
            val = perline_noise_spot_patial(sample_x, sample_y, num_octaves)

            color: float = (val + 1.0) * 0.5
            pixels[y, x] = color

            pixels[y, x] = color
    # del pixels
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
    # return pixels
    del pixels


def display_noise(pixels: list[NDArray[np.double]]) -> None:
    """Displays the perlin noise maps(pixels) in a matplotlib plot"""
    n = len(pixels)
    sn = math.ceil(math.sqrt(n))
    fig, axs = plt.subplots(sn, sn, figsize=(10, 8), sharex=True)  # type: ignore

    for i in range(n):
        ridx = i // sn
        cidx = i % sn
        axs[ridx, cidx].imshow(pixels[i], cmap="gray", interpolation="nearest")  # type: ignore
        axs[ridx, cidx].axis("off")
    for i in range(n, sn**2):
        ridx = i // sn
        cidx = i % sn
        axs[ridx, cidx].axis("off")
    fig.suptitle("Noise maps", fontsize=16)  # type: ignore
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # type: ignore
    plt.show()


def plot_hist(pixels: list[NDArray[np.double]]) -> None:
    plt.hist(np.concatenate(pixels).flatten(), 100)
    plt.show()


def k_th_percent(perc: float, xs: list[float]):
    sl = sorted(xs)
    idx = int(perc * len(xs))
    return sl[idx]


def main() -> None:
    window_width: int = 25
    window_height: int = 25

    pixels: list[NDArray[np.double]] = []
    for i in range(16):
        pixels.append(
            perlin_noise(window_width, window_height, (i + 1) * 1, 15, (i * 50, 2))
        )

    display_noise(pixels)
    plot_hist(pixels)
    vals = list(np.concatenate(pixels).flatten())
    print(k_th_percent(0.9, vals))

    display_noise(list(map(lambda x: x > 0.646, pixels)))


k = 10_000


def gen_data() -> tuple[int, int]:
    return random.randint(-k, k), random.randint(-k, k)


def id[T](x: T) -> T:
    return x


if __name__ == "__main__":
    main()
    print("")
    s = 25
    fr = 5
    perf_tester = PerformanceTester(10, gen_data)
    perf_tester.add_function("perl", lambda x: perlin_noise(s, s, 20, fr, x), id)
    perf_tester.add_function("perl_mp", lambda x: perlin_noise_mp(s, s, 20, fr, x), id)
    perf_tester.compare_performance()
