import math

import pytest

from roboarena.shared.utils.vector import Vector

VF = Vector[float]
VFFix = list[VF]


def random_vector() -> VF:
    import random

    return Vector(random.randint(-10_000, 10_000), random.randint(-10_000, 10_000))


@pytest.fixture
def vectors() -> VFFix:
    return [random_vector() for _ in range(100)]


def isclose(a: VF, b: VF) -> bool:
    return a == b


def test_commutativity_addition(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        assert isclose(a + b, b + a)


def test_associativity_addition(vectors: VFFix) -> None:
    for vector in vectors:
        a, b, c = vector, random_vector(), random_vector()
        assert isclose(a + (b + c), (a + b) + c)


def test_identity_addition(vectors: VFFix) -> None:
    zero_vector = Vector(0, 0)
    for vector in vectors:
        assert isclose(vector + zero_vector, vector)


def test_inverse_addition(vectors: VFFix) -> None:
    zero_vector = Vector(0.0, 0)
    for vector in vectors:
        neg_vector = zero_vector - vector
        assert isclose(vector + neg_vector, zero_vector)


def test_commutativity_multiplication(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        assert isclose(a * b, b * a)


def test_associativity_multiplication(vectors: VFFix) -> None:
    for vector in vectors:
        a, b, c = vector, random_vector(), random_vector()
        assert isclose(a * (b * c), (a * b) * c)


def test_identity_multiplication(vectors: VFFix) -> None:
    one_vector = Vector(1, 1)
    for vector in vectors:
        assert isclose(vector * one_vector, vector)


def test_distributivity(vectors: VFFix) -> None:
    for vector in vectors:
        a, b, c = vector, random_vector(), random_vector()
        assert isclose(a * (b + c), (a * b) + (a * c))


def test_inverse_division(vectors: VFFix) -> None:
    one_vector = Vector(1.0, 1)
    for vector in vectors:
        assert isclose(vector / vector, one_vector)


def test_dot_product(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        dot = a.x * b.x + a.y * b.y
        assert isclose(Vector(dot, dot), Vector(a.dot_product(b), a.dot_product(b)))


def test_length(vectors: VFFix) -> None:
    for vector in vectors:
        length = (vector.x**2 + vector.y**2) ** 0.5
        assert abs(vector.length() - length) < 1e-6


def test_normalize(vectors: VFFix) -> None:
    for vector in vectors:
        if vector.length() == 0:
            continue  # Skip the zero vector
        normalized = vector.normalize()
        assert abs(normalized.length() - 1) < 1e-6


def test_floor(vectors: VFFix) -> None:
    for vector in vectors:
        floored = vector.floor()
        assert floored.x == math.floor(vector.x) and floored.y == math.floor(vector.y)


def test_ceil(vectors: VFFix) -> None:
    for vector in vectors:
        ceiled = vector.ceil()
        assert ceiled.x == math.ceil(vector.x) and ceiled.y == math.ceil(vector.y)


def test_round(vectors: VFFix) -> None:
    for vector in vectors:
        rounded = vector.round()
        assert rounded.x == round(vector.x) and rounded.y == round(vector.y)


def test_distance_to(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        distance = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
        assert abs(a.distance_to(b) - distance) < 1e-6


def test_any_leq(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        assert vector.any_leq(b) == (a.x <= b.x or a.y <= b.y)


def test_any_geq(vectors: VFFix) -> None:
    for vector in vectors:
        a, b = vector, random_vector()
        assert vector.any_geq(b) == (a.x >= b.x or a.y >= b.y)


def test_mirror(vectors: VFFix) -> None:
    for vector in vectors:
        mirrored = vector.mirror()
        assert mirrored.x == vector.y and mirrored.y == vector.x


def test_to_tuple(vectors: VFFix) -> None:
    for vector in vectors:
        tup = vector.to_tuple()
        assert tup == (vector.x, vector.y)


def test_from_tuple(vectors: VFFix) -> None:
    for vector in vectors:
        tup = vector.to_tuple()
        recreated_vector = Vector.from_tuple(tup)
        assert recreated_vector == vector


def test_vector2_repr(vectors: VFFix) -> None:
    from pygame import Vector2

    for vector in vectors:
        v2 = vector.vector2_repr()
        assert v2 == Vector2(vector.x, vector.y)
