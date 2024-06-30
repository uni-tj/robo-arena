import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from random import getrandbits
from typing import Any, Callable, Generator, NoReturn, Tuple

import numpy as np
import pygame

from roboarena.shared.utils.vector import Vector


def gen_id(ids: Iterable[int]) -> int:
    """Generate a new 32bit id distinct from the given ids"""
    while True:
        next_id = getrandbits(32)
        if next_id in ids:
            continue
        return next_id


type Counter = Generator[int, Any, NoReturn]


def counter():
    next = 0
    while True:
        yield next
        next += 1


def gen_coord_space(
    xbounds: tuple[int, int], ybounds: tuple[int, int]
) -> list[Vector[int]]:
    """Generates a list of coordinates in the rectangle given by xbounds and ybounds

    Args:
        xbounds (tuple[int, int]): (min x val, max x val)
        ybounds (tuple[int, int]): (min y val, may y val)

    Returns:
        list[Vector[int]]: list of Vector coordinates
            in the space defined by xbounds and ybounds
    """
    lnx = np.linspace(xbounds[0], xbounds[1] - 1, xbounds[1] - xbounds[0])
    lny = np.linspace(ybounds[0], ybounds[1] - 1, ybounds[1] - ybounds[0])
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    return [Vector.from_sequence(coord) for coord in coords]


def enumerate2d[T](iter: Iterable[Iterable[T]]) -> Iterable[tuple[tuple[int, int], T]]:
    return [((i, j), v) for i, row in enumerate(iter) for j, v in enumerate(row)]


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


def gradientRect(
    window: pygame.Surface,
    left_colour: Tuple[int, int, int],
    right_colour: Tuple[int, int, int],
    target_rect: pygame.Rect,
):
    colour_rect = pygame.Surface((2, 2))
    pygame.draw.line(colour_rect, left_colour, (0, 0), (1, 0))
    pygame.draw.line(colour_rect, right_colour, (0, 1), (1, 1))
    colour_rect: pygame.Surface = pygame.transform.smoothscale(
        colour_rect, target_rect.size
    )
    window.blit(colour_rect, target_rect)


def graphic_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "resources", "graphics", path)


def load_graphic(path: str) -> pygame.Surface:
    return pygame.image.load(graphic_path(path))


class EventTarget[Evt]:
    """Class for emiting and listening to events.

    Event handlers are called synchronousely.

    Inheriting from this class is discouraged. Rather keep it as property `events`.
    """

    _logger = logging.getLogger(f"{__name__}.EventTarget")
    """Dict from reference to original listener to internal listener"""
    _listeners: dict[Callable[[Any], None], Callable[[Evt], None]]

    def __init__(self) -> None:
        self._listeners = {}

    def add_listener[S](self, typ: type[S], listener: Callable[[S], None]):
        def _listener(e: Evt):
            if isinstance(e, typ):
                listener(e)

        self._listeners[listener] = _listener

    def remove_listener(self, listener: Callable[[Evt], None]):
        del self._listeners[listener]

    def dispatch(self, event: Evt) -> None:
        for listener in self._listeners.values():
            listener(event)


class Stoppable(ABC):
    """Interface for objects supporting being stopped from another thread"""

    @abstractmethod
    def stop(self) -> None: ...


def stopAll(*stoppables: Stoppable) -> None:
    for stoppable in stoppables:
        stoppable.stop()


@dataclass(frozen=True)
class Stopped:
    pass
