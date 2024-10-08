from math import ceil, floor
from typing import Callable, Tuple, Union, overload

# Define the type for float-based tuples
type TupleVector = tuple[float, float]
"""Provides function most arithmetic operation for float-based tuple Vectors."""


@overload
def add_tuples(a: TupleVector, b: float) -> TupleVector: ...
@overload
def add_tuples(a: TupleVector, b: TupleVector) -> TupleVector: ...


def add_tuples(a: TupleVector, b: Union[TupleVector, float]) -> TupleVector:
    if isinstance(b, tuple):
        return (a[0] + b[0], a[1] + b[1])
    else:
        return (a[0] + b, a[1] + b)


@overload
def sub_tuples(a: TupleVector, b: float) -> TupleVector: ...
@overload
def sub_tuples(a: TupleVector, b: TupleVector) -> TupleVector: ...


def sub_tuples(a: TupleVector, b: Union[TupleVector, float]) -> TupleVector:
    if isinstance(b, tuple):
        return (a[0] - b[0], a[1] - b[1])
    else:
        return (a[0] - b, a[1] - b)


@overload
def mul_tuples(a: TupleVector, b: float) -> TupleVector: ...
@overload
def mul_tuples(a: TupleVector, b: TupleVector) -> TupleVector: ...


def mul_tuples(a: TupleVector, b: Union[TupleVector, float]) -> TupleVector:
    if isinstance(b, tuple):
        return (a[0] * b[0], a[1] * b[1])
    else:
        return (a[0] * b, a[1] * b)


@overload
def truediv_tuples(a: TupleVector, b: float) -> TupleVector: ...
@overload
def truediv_tuples(a: TupleVector, b: TupleVector) -> TupleVector: ...


def truediv_tuples(a: TupleVector, b: Union[TupleVector, float]) -> TupleVector:
    if isinstance(b, tuple):
        return (a[0] / b[0], a[1] / b[1])
    else:
        return (a[0] / b, a[1] / b)


def round_tuples(a: TupleVector) -> Tuple[int, int]:
    return (round(a[0]), round(a[1]))


def floor_tuples(a: TupleVector) -> Tuple[int, int]:
    return (floor(a[0]), floor(a[1]))


def ceil_tuples(a: TupleVector) -> Tuple[int, int]:
    return (ceil(a[0]), ceil(a[1]))


def apply_transform_tuples(
    a: TupleVector, f: Callable[[float], float] = lambda x: x
) -> TupleVector:
    return (f(a[0]), f(a[1]))


def eq_tuples(a: TupleVector, b: TupleVector) -> bool:
    return a[0] == b[0] and a[1] == b[1]
