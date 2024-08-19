import random

import pytest

from roboarena.shared.utils.tuple_vec import (
    VectorFloat,
    add_tuples,
    apply_transform_tuples,
    eq_tuples,
    mul_tuples,
    round_tuples,
    sub_tuples,
    truediv_tuples,
)

type TVF = VectorFloat


def ri(b: float = 1_000) -> float:
    return random.uniform(-b, b)


def rt(b: float = 1_000) -> TVF:
    return (ri(b), ri(b))


type Fix = list[TVF]
type Inp = list[Fix]


TVZERO = (0, 0)
TVONE = (1, 1)


@pytest.fixture
def inp() -> Inp:
    return [[rt() for _ in range(5)] for _ in range(100)]


def isclose(a: TVF, b: TVF, epsilon: float = 1e-3) -> bool:
    return abs(a[0] - b[0]) < epsilon and abs(a[1] - b[1]) < epsilon


def test_commutativity_addition(inp: Inp):
    for vectors in inp:
        a, b, *_ = vectors
        assert isclose(add_tuples(a, b), add_tuples(b, a))


def test_associativity_addition(inp: Inp):
    for vectors in inp:
        a, b, c, *_ = vectors
        assert isclose(add_tuples(a, add_tuples(b, c)), add_tuples(add_tuples(a, b), c))


def test_identity_addition(inp: Inp):
    for vectors in inp:
        a, *_ = vectors

        assert isclose(add_tuples(a, TVZERO), a)


def test_inverse_addition(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        neg_a = sub_tuples(TVZERO, a)
        assert isclose(add_tuples(a, neg_a), TVZERO)


def test_commutativity_multiplication(inp: Inp):
    for vectors in inp:
        a, b, *_ = vectors
        assert isclose(mul_tuples(a, b), mul_tuples(b, a))


def test_associativity_multiplication(inp: Inp):
    for vectors in inp:
        a, b, c, *_ = vectors
        assert isclose(mul_tuples(a, mul_tuples(b, c)), mul_tuples(mul_tuples(a, b), c))


def test_identity_multiplication(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        assert isclose(mul_tuples(a, TVONE), a)


def test_distributivity(inp: Inp):
    for vectors in inp:
        a, b, c, *_ = vectors
        assert isclose(
            mul_tuples(a, add_tuples(b, c)),
            add_tuples(mul_tuples(a, b), mul_tuples(a, c)),
        )


def test_inverse_division(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        assert isclose(truediv_tuples(a, a), TVONE)


def test_round_tuples(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        assert round_tuples(a) == (round(a[0]), round(a[1]))


def test_apply_transform(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        assert isclose(
            apply_transform_tuples(a, lambda x: x**2), (a[0] ** 2, a[1] ** 2)
        )


def test_equality(inp: Inp):
    for vectors in inp:
        a, *_ = vectors
        assert eq_tuples(a, a) is True
