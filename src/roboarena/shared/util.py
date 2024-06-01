from collections.abc import Iterable
from random import getrandbits
from typing import Any, Callable

import numpy as np

from roboarena.shared.utils.vector import Vector


def gen_id(ids: Iterable[int]) -> int:
    """Generate a new 32bit id distinct from the given ids"""
    while True:
        next_id = getrandbits(32)
        if next_id in ids:
            continue
        return next_id


def counter():
    next = 0
    while True:
        yield next
        next += 1


def gen_coord_space(xsize: int, ysize: int) -> list[Vector[int]]:
    vects = []
    lnx = np.linspace(0, xsize - 1, xsize)  # type: ignore
    lny = np.linspace(0, ysize - 1, ysize)  # type: ignore
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    def toVect2(x) -> Vector:  # type: ignore
        return Vector(x[0], x[1])  # type: ignore

    for coord in coords:
        vects.append(toVect2(coord))  # type: ignore
    return vects  # type: ignore


def dict_diff_keys[K, V](dict1: dict[K, V], dict2: dict[K, V]) -> dict[K, V]:
    diff_keys = set(dict1.keys()) ^ set(dict2.keys())
    diff_dict: dict[K, V] = {}
    for key in diff_keys:
        if key in dict1:
            diff_dict[key] = dict1[key]
        else:
            diff_dict[key] = dict2[key]

    return diff_dict


def getBounds(position: list[Vector[int]]) -> tuple[Vector[int], Vector[int]]:
    max_x = max(position, key=lambda x: x.x).x
    min_x = min(position, key=lambda x: x.x).x
    max_y = max(position, key=lambda x: x.y).y
    min_y = min(position, key=lambda x: x.y).y
    return (Vector(min_x, min_y), Vector(max_x, max_y))


class EventTarget[Evt]:
    _listeners: dict[Callable[[Any], None], Callable[[Evt], None]] = {}

    def add_event_listener[S](self, typ: type[S], listener: Callable[[S], None]):
        def _listener(e: Evt):
            if isinstance(e, typ):
                listener(e)

        self._listeners[listener] = _listener

    def remove_event_listener(self, listener: Callable[[Evt], None]):
        del self._listeners[listener]

    def dispatch_event(self, event: Evt) -> None:
        for listener in self._listeners:
            listener(event)
