from math import degrees

from roboarena.shared.utils.vector import Vector


def assert_close(actual: float, expected: float, epsilon: float = 0.001):
    assert abs(expected - actual) < epsilon


def test_dot_orth():
    res = Vector.dot(Vector(0, -1), Vector(1, 0))
    assert_close(res, 0)


def test_dot_45():
    res = Vector.dot(Vector(1, 1).normalize(), Vector(1, 0))
    assert res > 0 and res < 1


def test_angle_0():
    res = Vector.angle(Vector(1, 0), Vector(1, 0))
    assert_close(degrees(res), 0)


def test_angle_45():
    res = Vector.angle(Vector(1, -1), Vector(1, 0))
    assert_close(degrees(res), 45)


def test_angle_90():
    res = Vector.angle(Vector(0, -1), Vector(1, 0))
    assert_close(degrees(res), 90)


def test_angle_neg():
    res = Vector.angle(Vector(0, 1), Vector(1, 0))
    assert_close(degrees(res), -90)
