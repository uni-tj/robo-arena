import heapq
import logging
import os
import string
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from itertools import count
from random import getrandbits
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

import numpy as np
import pygame
from attrs import define
from numpy.typing import NDArray
from pygame import Surface

from roboarena.shared.time import get_time
from roboarena.shared.types import StartFrameEvent, Time
from roboarena.shared.utils.vector import Vector

if TYPE_CHECKING:
    from roboarena.shared.game import GameState


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


def safe_next[T](iterator: Iterator[T]) -> T | None:
    try:
        return next(iterator)
    except StopIteration:
        return None


@cache
def rect_space(bottom_right: Vector[int]) -> Iterable[Vector[int]]:
    """Generates a list of coordinates in the rectangle given by xbounds and ybounds

    Args:
        size: Vector[int]  the Rectangle size starting at 0,0

    Returns:
        list[Vector[int]]: list of coordinates in the space
            defined by l_bounds and u_bounds
    """
    lnx = np.linspace(0, bottom_right.x, bottom_right.x + 1)
    lny = np.linspace(0, bottom_right.y, bottom_right.y + 1)
    coords = np.array(np.meshgrid(lnx, lny)).ravel("F").reshape(-1, 2).astype(int)

    return [Vector.from_sequence(coord) for coord in coords]


def rect_space_at(
    top_left: Vector[int], bottom_right: Vector[int]
) -> Iterable[Vector[int]]:
    return (top_left + pos for pos in rect_space(bottom_right - top_left))


@cache
def rect_space_cached_at(
    top_left: Vector[int], bottom_right: Vector[int]
) -> list[Vector[int]]:
    return [top_left + pos for pos in rect_space(bottom_right - top_left)]


def square_space(apothem: int) -> Iterable[Vector[int]]:
    return rect_space_at(Vector.from_scalar(-apothem), Vector.from_scalar(apothem))


@cache
def square_space_around(center: Vector[int], apothem: int) -> list[Vector[int]]:
    return [(pos + center).round() for pos in square_space(apothem)]


def spiral_space() -> Iterable[Vector[int]]:
    yield Vector(0, 0)
    for apothem in count(start=1):
        for i in range(2 * apothem):
            yield Vector(-apothem + i, -apothem)
        for i in range(2 * apothem):
            yield Vector(apothem, -apothem + i)
        for i in range(2 * apothem):
            yield Vector(apothem - i, apothem)
        for i in range(2 * apothem):
            yield Vector(-apothem, apothem - i)


def enumerate2d[T](iter: Iterable[Iterable[T]]) -> Iterable[tuple[tuple[int, int], T]]:
    return (((i, j), v) for i, row in enumerate(iter) for j, v in enumerate(row))


def enumerate2d_vec[T](iter: Iterable[Iterable[T]]) -> Iterable[tuple[Vector[int], T]]:
    return ((Vector.from_tuple(coord), v) for coord, v in enumerate2d(iter))


def map2d[
    T, U
](f: Callable[[T], U], xss: Iterable[Iterable[T]]) -> Iterable[Iterable[U]]:
    return ((f(x) for x in xs) for xs in xss)


def neighbours_horiz[T](matrix: Iterable[Iterable[T]]) -> Iterable[tuple[T, T]]:
    """
    Returns all (left, right) pairs of horiz. neighbouring elements in a matrix

    Rows of matrix may have different length.
    """
    for row in matrix:
        iterator = iter(row)
        left = safe_next(iterator)
        if left is None:
            continue
        for right in iterator:
            yield (left, right)
            left = right


def neighbours_vert[T](matrix: Iterable[Iterable[T]]) -> Iterable[tuple[T, T]]:
    """
    Returns all (top, bottom) pairs of vert. neighbouring elements in a matrix

    Rows of matrix may have different length.
    """
    iterator = iter(matrix)
    top_row = safe_next(iterator)
    if top_row is None:
        return
    for bottom_row in iterator:
        for n in zip(top_row, bottom_row):
            yield n
        top_row = bottom_row


class Neighbours4(Enum):
    TOP = Vector(0, -1)
    RIGHT = Vector(1, 0)
    BOTTOM = Vector(0, 1)
    LEFT = Vector(-1, 0)


def neighbours_4(position: Vector[int]) -> Iterable[Vector[int]]:
    return (position + neigh.value for neigh in Neighbours4)


def flatten[T](xss: Iterable[Iterable[T]]) -> Iterable[T]:
    return (x for xs in xss for x in xs)


def flatmap[T](f: Callable[[T], Iterable[T]], xs: Iterable[T]) -> Iterable[T]:
    return (y for x in xs for y in f(x))


def dedupe[T](xs: Iterable[T]) -> Iterable[T]:
    """Deduplicate xs. Algorithm is stable."""
    seen = set[T]()
    for x in xs:
        if x in seen:
            continue
        yield x
        seen.add(x)


def search_connected[
    P, D, L
](
    start: P,
    data: dict[P, D],
    label: Callable[[D], Optional[L]],
    neighbours: Callable[[P], Iterable[P]],
) -> Mapping[P, L]:
    queue = deque[P]([start])
    found = dict[P, L]()
    while len(queue) > 0:
        p = queue.pop()
        if p in found:
            continue
        if p not in data:
            continue
        l = label(data[p])
        if l is None:
            continue
        found[p] = l
        queue += neighbours(p)
    return found


def get_min_max[
    T: (float, int)
](points: Iterable[Vector[T]]) -> tuple[Vector[T], Vector[T]]:

    min_pos = Vector(min(p.x for p in points), min(p.y for p in points))
    max_pos = Vector(max(p.x for p in points), max(p.y for p in points))
    return min_pos, max_pos


def print_points(points: Iterable[Vector[int]]):
    labels = string.digits + string.ascii_letters
    min_pos, max_pos = get_min_max(points)
    dim = max_pos - min_pos + 1
    matrix = [["#" for _ in range(dim.x)] for _ in range(dim.y)]
    for i, point in enumerate(points):
        matrix[point.y - min_pos.y][point.x - min_pos.x] = labels[i % len(labels)]
    print("\n".join(["".join(row) for row in matrix]))


def gradientRect(
    window: pygame.Surface,
    left_colour: tuple[int, int, int],
    right_colour: tuple[int, int, int],
    target_rect: pygame.Rect,
):
    colour_rect = pygame.Surface((2, 2))
    pygame.draw.line(colour_rect, left_colour, (0, 0), (1, 0))
    pygame.draw.line(colour_rect, right_colour, (0, 1), (1, 1))
    colour_rect: pygame.Surface = pygame.transform.smoothscale(
        colour_rect, target_rect.size
    )
    window.blit(colour_rect, target_rect)


def rotate(surface: Surface, angle: float, pivot: tuple[int, int]) -> Surface:
    w, h = surface.get_size()
    surface2 = Surface((2 * w, 2 * h), pygame.SRCALPHA)
    surface2.blit(surface, (w - pivot[0], h - pivot[1]))
    return pygame.transform.rotate(surface2, angle)


def resource_path(relative_path: str) -> str:
    """Get the absolute path to the resource"""
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "resources")
    )

    return os.path.join(base_path, relative_path.replace("/", os.sep))


def graphic_path(path: str) -> str:
    return resource_path(os.path.join("graphics", path))


def sound_path(path: str) -> str:
    return resource_path(os.path.join("sounds", path))


def load_graphic(path: str) -> pygame.Surface:
    return pygame.image.load(graphic_path(path))


def frame_cache(game: "GameState"):
    """
    Like functools.cache, but resets cache every frame.

    Can be used on instance methods, as `self` references are cleared reguarly.
    """

    def decorator[**P, R](f: Callable[P, R]) -> Callable[P, R]:  # noqa: F821
        cached_f = cache(f)

        def reset_cached_f():
            nonlocal cached_f
            cached_f = cache(f)

        game.events.add_listener(StartFrameEvent, lambda e: reset_cached_f())

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
            return cached_f(*args, **kwargs)

        return wrapper

    return decorator


def frame_cache_method[**P, R](f: Callable[P, R]) -> Callable[P, R]:  # noqa: F821
    """Like frame_cache for instance methods with `self._game: GameState` present"""
    cached_f: Optional[Callable[P, R]] = None  # noqa: F821

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
        nonlocal cached_f
        if cached_f is None:
            cached_f = frame_cache(args[0]._game)(f)  # type: ignore
        return cached_f(*args, **kwargs)

    return wrapper


def debounce(seconds: Time):
    def decorator[**P, R](f: Callable[P, R]) -> Callable[P, R | None]:
        last_call: Time = 0

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            nonlocal last_call
            if get_time() - last_call < seconds:
                last_call = get_time()
                return
            last_call = get_time()
            return f(*args, **kwargs)

        return wrapper

    return decorator


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

    def remove_listener(self, listener: Callable[[Any], None]):
        del self._listeners[listener]

    def dispatch(self, event: Evt) -> None:
        for listener in self._listeners.values():
            listener(event)


def throws(exception: type[Exception], f: Callable[[], Any]):
    try:
        f()
        return False
    except exception:
        return True


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


@dataclass
class Tag[K: (int, float), T]:
    key: K
    value: T

    def __lt__(self, other: "Tag[K, T]"):
        return self.key < other.key


@dataclass
class Heap[T](Collection[T]):
    heap: list[T] = field(default_factory=list)

    def __iter__(self) -> Iterator[T]:
        return iter(self.heap)

    def __len__(self) -> int:
        return len(self.heap)

    def __contains__(self, x: object) -> bool:
        return x in self.heap

    def push(self, item: T) -> None:
        heapq.heappush(self.heap, item)

    def pop(self) -> T:
        return heapq.heappop(self.heap)

    def smallest(self) -> T:
        return self.heap[0]

    def nlargest(self, n: int) -> list[T]:
        return heapq.nlargest(n, self.heap)

    def nsmallest(self, n: int) -> list[T]:
        return heapq.nsmallest(n, self.heap)


@define
class change_exception:
    """
    Replace a certain exception type by another in a code block.

    .. code-block:: python
        # Will throw ValueError:
        with change_exception(KeyError, ValueError):
            {1: True}[0]
    """

    from_exc: type[Exception]
    to_exc: Callable[[], Exception]

    def __enter__(self):
        pass

    def __exit__(self, exc_type: type | None, exc_value: Any, traceback: Any):
        if exc_type == self.from_exc:
            raise self.to_exc()


@define
class exceqt:
    """
    Catch an exception and perform an action.

    .. code-block:: python
        with _except(ValueError, lambda: print("catched")):
            ...
        # is equivalent to
        try:
            ...
        except ValueError:
            print("catched")
    """

    exc_type: type[Exception]
    on_exc: Callable[[], Any]

    def __enter__(self):
        pass

    def __exit__(self, exc_type: type | None, exc_value: Any, traceback: Any):
        if exc_type == self.exc_type:
            self.on_exc()
            return True


class Color(Enum):
    RED = "\033[31m"
    RED_BG = "\033[41m"
    GREEN = "\033[32m"
    GREEN_BG = "\033[42m"
    BLUE = "\033[34m"
    BLUE_BG = "\033[44;30m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_BLUE_BG = "\033[104;30m"
    CYAN = "\033[36m"
    CYAN_BG = "\033[46;30m"
    NONE = ""


def color(str: str, color: Color) -> str:
    return f"{color.value}{str}\033[0m"


type Barr = NDArray[np.bool_]


def nd_arr2int(arr: Barr) -> int:
    return int("".join(map(str, arr.astype(int))), 2)


def int2nd_arr(value: int, size: int) -> Barr:
    binary_string = bin(value)[2:].zfill(size)
    return np.array(list(map(int, binary_string)), dtype=np.bool_)


def nonzero_inv(values: Iterable[int]) -> int:
    """
    Returns an int where all bits given by the indices in values are non-zero.

    .. code-block:: python
        nonzero_inv([0,3]) == 0b1001
    """
    result = 0
    for value in values:
        result |= 1 << value
    return result


def nonzero(value: int) -> list[int]:
    """
    Returns the list of non-zero bits.

    .. code-block:: python
        nonzero(0b1001) == [0,3]
    """
    result = list[int]()
    i = 0
    while value > 0:
        if value & 1:
            result.append(i)
        value >>= 1
        i += 1
    return result


def nonzerop(value: int) -> Iterable[int]:
    """
    Returns the list of non-zero bits.

    .. code-block:: python
        nonzero(0b1001) == [0,3]
    """
    i = 0
    while value > 0:
        if value & 1:
            yield i
        value >>= 1
        i = i + 1


def nonzero_count(value: int) -> int:
    """
    Returns the number of non-zero bits.

    ..code-block:: python
        nonzero_count(0b1001) == 2
    """
    count = 0
    while value > 0:
        count = (value & 1) + count
        value >>= 1
    return count


def ones(n: int) -> int:
    """
    Returns an int where last n bits are 1.

    ..code-block:: python
        ones(4) == 0b1111
    """
    return (1 << n) - 1


def one_hot(k: int) -> int:
    """
    Returns an int only bit k is 1.

    ..code-block:: python
        one_hot(4) == 0b1000
    """
    return 1 << k


def ones_except(n: int, k: int) -> int:
    """
    Returns an int where last n bits are 1 except bit k.

    ..code-block:: python
        ones_except(4, 1) == 0b1101
    """
    return ((1 << n) - 1) ^ (1 << k)


def is_one_at(value: int, k: int) -> bool:
    """
    Returns whether bit k of value is 1.

    ..code-block:: python
        is_one_at(0b1101, 2) == True
        is_one_at(0b1101, 1) == False
    """
    return (value >> k) & 1 == 1
