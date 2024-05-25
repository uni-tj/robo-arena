import numpy as np
from vector import Vector


def gen_coord_space(xsize: int, ysize: int) -> list[Vector[int]]:
    vects = []
    lnx = np.linspace(0, xsize - 1, xsize)  # type: ignore
    lny = np.linspace(0, ysize - 1, ysize)  # type: ignore
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    def toVect2(x) -> Vector:
        return Vector(x[0], x[1])

    for coord in coords:
        vects.append(toVect2(coord))
    return vects
