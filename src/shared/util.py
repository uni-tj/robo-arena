from random import getrandbits
from collections.abc import Iterable


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
