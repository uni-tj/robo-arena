import math
from typing import List

import pytest

from roboarena.shared.utils.vector import Matrix2d, Vector

MF = Matrix2d[float] | Matrix2d[int]
MFFix = List[MF]
VF = Vector[float]


def random_matrix() -> MF:
    import random

    return Matrix2d(
        random.uniform(-10, 10),
        random.uniform(-10, 10),
        random.uniform(-10, 10),
        random.uniform(-10, 10),
    )


def random_vector() -> VF:
    import random

    return Vector(random.uniform(-10, 10), random.uniform(-10, 10))


@pytest.fixture
def matrices() -> MFFix:
    return [random_matrix() for _ in range(100)]


def isclose(a: MF, b: MF, rel_tol: float = 1e-09, abs_tol: float = 1e-09) -> bool:
    return (
        math.isclose(a.a11, b.a11, rel_tol=rel_tol, abs_tol=abs_tol)
        and math.isclose(a.a12, b.a12, rel_tol=rel_tol, abs_tol=abs_tol)
        and math.isclose(a.a21, b.a21, rel_tol=rel_tol, abs_tol=abs_tol)
        and math.isclose(a.a22, b.a22, rel_tol=rel_tol, abs_tol=abs_tol)
    )


def test_commutativity_addition(matrices: MFFix) -> None:
    for matrix in matrices:
        a, b = matrix, random_matrix()
        assert isclose(a + b, b + a)


def test_associativity_addition(matrices: MFFix) -> None:
    for matrix in matrices:
        a, b, c = matrix, random_matrix(), random_matrix()
        assert isclose(a + (b + c), (a + b) + c)


def test_identity_addition(matrices: MFFix) -> None:
    zero_matrix = Matrix2d(0, 0, 0, 0)
    for matrix in matrices:
        assert isclose(matrix + zero_matrix, matrix)


def test_inverse_addition(matrices: MFFix) -> None:
    zero_matrix = Matrix2d(0, 0, 0, 0)
    for matrix in matrices:
        neg_matrix = zero_matrix - matrix
        assert isclose(matrix + neg_matrix, zero_matrix)


def test_associativity_multiplication(matrices: MFFix) -> None:
    for matrix in matrices:
        a, b, c = matrix, random_matrix(), random_matrix()
        assert isclose(a * (b * c), (a * b) * c)


def test_identity_multiplication(matrices: MFFix) -> None:
    identity_matrix = Matrix2d.identity()
    for matrix in matrices:
        assert isclose(matrix * identity_matrix, matrix)
        assert isclose(identity_matrix * matrix, matrix)


def test_distributivity_matrix_addition(matrices: MFFix) -> None:
    for matrix in matrices:
        a, b, c = matrix, random_matrix(), random_matrix()
        assert isclose(a * (b + c), (a * b) + (a * c))


def test_distributivity_scalar_multiplication(matrices: MFFix) -> None:
    for matrix in matrices:
        a, b = matrix, random_matrix()
        scalar = random_vector().x
        assert isclose((a + b) * scalar, (a * scalar) + (b * scalar))


def test_matrix_vector_multiplication(matrices: MFFix) -> None:
    for matrix in matrices:
        vector = random_vector()
        result = matrix * vector
        expected = Vector(
            matrix.a11 * vector.x + matrix.a12 * vector.y,
            matrix.a21 * vector.x + matrix.a22 * vector.y,
        )
        assert result == expected


def test_transpose(matrices: MFFix) -> None:
    for matrix in matrices:
        transposed = matrix.transpose()
        assert transposed.a11 == matrix.a11
        assert transposed.a12 == matrix.a21
        assert transposed.a21 == matrix.a12
        assert transposed.a22 == matrix.a22


def test_determinant(matrices: MFFix) -> None:
    for matrix in matrices:
        det = matrix.determinant()
        expected = matrix.a11 * matrix.a22 - matrix.a12 * matrix.a21
        assert math.isclose(det, expected)


def test_inverse(matrices: MFFix) -> None:
    for matrix in matrices:
        if abs(matrix.determinant()) > 1e-6:
            inverse = matrix.inverse()
            identity = Matrix2d.identity()
            print(matrix * inverse, inverse * matrix)
            assert isclose(matrix * inverse, identity)
            assert isclose(inverse * matrix, identity)


def test_rotation_matrix(matrices: MFFix) -> None:
    for _ in range(100):
        angle = random_vector().x
        rot_matrix = Matrix2d.rot_matrix(angle)
        assert math.isclose(rot_matrix.determinant(), 1, rel_tol=1e-9)
        assert isclose(rot_matrix * rot_matrix.transpose(), Matrix2d.identity())


def test_scale_matrix(matrices: MFFix) -> None:
    for _ in range(100):
        sx, sy = random_vector().x, random_vector().y
        scale_matrix = Matrix2d.scale_matrix(sx, sy)
        assert scale_matrix.a11 == sx
        assert scale_matrix.a22 == sy
        assert scale_matrix.a12 == 0
        assert scale_matrix.a21 == 0


def test_shear_matrix(matrices: MFFix) -> None:
    for _ in range(100):
        shx, shy = random_vector().x, random_vector().y
        shear_matrix = Matrix2d.shear_matrix(shx, shy)
        assert shear_matrix.a11 == 1
        assert shear_matrix.a22 == 1
        assert shear_matrix.a12 == shx
        assert shear_matrix.a21 == shy
