import random
from functools import cache, wraps
from typing import Any, Callable, Optional

from roboarena.shared.utils.perf_tester import PerformanceTester


def id[T](x: T) -> T:
    return x


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

        game.events.add_listener(lambda e: reset_cached_f())

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
            return cached_f(*args, **kwargs)

        return wrapper

    return decorator


def frame_cache_method[**P, R](f: Callable[P, R]) -> Callable[P, R]:  # noqa: F821
    """Like frame_cache for instance methods with `self._game: GameState` present"""
    cached_f: Optional[Callable[P, R]] = None  # noqa: F821

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
        nonlocal cached_f
        if cached_f is None:
            cached_f = frame_cache(args[0]._game)(f)  # type: ignore
        return cached_f(*args, **kwargs)

    return wrapper


def frame_cache_no_wraps(game: "GameState"):
    """
    Like functools.cache, but resets cache every frame.

    Can be used on instance methods, as `self` references are cleared reguarly.
    """

    def decorator[**P, R](f: Callable[P, R]) -> Callable[P, R]:  # noqa: F821
        cached_f = cache(f)

        def reset_cached_f():
            nonlocal cached_f
            cached_f = cache(f)

        game.events.add_listener(lambda e: reset_cached_f())

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
            return cached_f(*args, **kwargs)

        return wrapper

    return decorator


def frame_cache_method_no_wraps[
    **P, R
](f: Callable[P, R]) -> Callable[P, R]:  # noqa: F821
    """Like frame_cache for instance methods with `self._game: GameState` present"""
    cached_f: Optional[Callable[P, R]] = None  # noqa: F821

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: F821
        nonlocal cached_f
        if cached_f is None:
            cached_f = frame_cache(args[0]._game)(f)  # type: ignore
        return cached_f(*args, **kwargs)

    return wrapper


class GameState:
    class Events:
        listeners = id

        def add_listener(self, f: Callable[[Any], Any]):
            self.listeners = f

    events: Events

    def __init__(self):
        self.events = self.Events()

    def tick(self):
        self.events.listeners("test")


class Test:
    _game: GameState

    def __init__(self) -> None:
        self._game = GameState()

    @frame_cache_method
    def test1(self, n: tuple[int, int]) -> int:
        x = n[0]
        for _ in range(n[1]):
            x *= n[0]
        return x

    @frame_cache_method_no_wraps
    def test2(self, n: tuple[int, int]) -> int:
        x = n[0]
        for _ in range(n[1]):
            x *= n[0]
        return x


if __name__ == "__main__":
    game_state = Test()

    def gen_data():
        return (random.randint(0, 200), random.randint(0, 200))

    tester = PerformanceTester(10_000_000, gen_data)

    @cache
    def test1(n: tuple[int, int]) -> int:
        x = n[0]
        for _ in range(n[1]):
            x *= n[0]
        return x

    def frame_test1(x: tuple[int, int]) -> int:
        res = game_state.test1(x)
        game_state._game.tick()
        return res

    def frame_test2(x: tuple[int, int]) -> int:
        res = game_state.test1(x)
        game_state._game.tick()
        return res

    # frame_test = lambda x: game_state.test1(x)

    tester.add_function("frame", frame_test1, id)
    tester.add_function("frame2", frame_test2, id)
    tester.add_function("functools", test1, id)
    tester.compare_performance()
