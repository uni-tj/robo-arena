from typing import Callable, Tuple, Union, overload

# Define the type for float-based tuples
type TupleVector = tuple[float, float]


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


def apply_transform_tuples(
    a: TupleVector, f: Callable[[float], float] = lambda x: x
) -> TupleVector:
    return (f(a[0]), f(a[1]))


def eq_tuples(a: TupleVector, b: TupleVector) -> bool:
    return a[0] == b[0] and a[1] == b[1]
