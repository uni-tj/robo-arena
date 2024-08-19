from typing import Callable, Tuple, Union, overload

# Define the type for float-based tuples
type VectorFloat = tuple[float, float]


@overload
def add_tuples(a: VectorFloat, b: float) -> VectorFloat: ...
@overload
def add_tuples(a: VectorFloat, b: VectorFloat) -> VectorFloat: ...


def add_tuples(a: VectorFloat, b: Union[VectorFloat, float]) -> VectorFloat:
    if isinstance(b, tuple):
        return (a[0] + b[0], a[1] + b[1])
    else:
        return (a[0] + b, a[1] + b)


@overload
def sub_tuples(a: VectorFloat, b: float) -> VectorFloat: ...
@overload
def sub_tuples(a: VectorFloat, b: VectorFloat) -> VectorFloat: ...


def sub_tuples(a: VectorFloat, b: Union[VectorFloat, float]) -> VectorFloat:
    if isinstance(b, tuple):
        return (a[0] - b[0], a[1] - b[1])
    else:
        return (a[0] - b, a[1] - b)


@overload
def mul_tuples(a: VectorFloat, b: float) -> VectorFloat: ...
@overload
def mul_tuples(a: VectorFloat, b: VectorFloat) -> VectorFloat: ...


def mul_tuples(a: VectorFloat, b: Union[VectorFloat, float]) -> VectorFloat:
    if isinstance(b, tuple):
        return (a[0] * b[0], a[1] * b[1])
    else:
        return (a[0] * b, a[1] * b)


@overload
def truediv_tuples(a: VectorFloat, b: float) -> VectorFloat: ...
@overload
def truediv_tuples(a: VectorFloat, b: VectorFloat) -> VectorFloat: ...


def truediv_tuples(a: VectorFloat, b: Union[VectorFloat, float]) -> VectorFloat:
    if isinstance(b, tuple):
        return (a[0] / b[0], a[1] / b[1])
    else:
        return (a[0] / b, a[1] / b)


def round_tuples(a: VectorFloat) -> Tuple[int, int]:
    return (round(a[0]), round(a[1]))


def apply_transform_tuples(
    a: VectorFloat, f: Callable[[float], float] = lambda x: x
) -> VectorFloat:
    return (f(a[0]), f(a[1]))


def eq_tuples(a: VectorFloat, b: VectorFloat) -> bool:
    return a[0] == b[0] and a[1] == b[1]
