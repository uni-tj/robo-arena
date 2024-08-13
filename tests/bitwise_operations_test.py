from roboarena.shared.util import (
    is_one_at,
    nonzero,
    nonzero_count,
    nonzero_inv,
    one_hot,
    ones,
    ones_except,
)


def test_nonzero_inv():
    assert nonzero_inv([0, 3]) == 0b1001
    assert nonzero_inv([1, 2, 4]) == 0b10110
    assert nonzero_inv([5]) == 0b100000
    assert nonzero_inv([]) == 0b0
    assert nonzero_inv([0, 1, 2, 3, 4, 5, 6, 7]) == 0b11111111


def test_nonzero():
    assert nonzero(0b1001) == [0, 3]
    assert nonzero(0b1110) == [1, 2, 3]
    assert nonzero(0b100000) == [5]
    assert nonzero(0b0) == []
    assert nonzero(0b11111111) == [0, 1, 2, 3, 4, 5, 6, 7]


def test_nonzero_count():
    assert nonzero_count(0b1001) == 2
    assert nonzero_count(0b1110) == 3
    assert nonzero_count(0b100000) == 1
    assert nonzero_count(0b0) == 0
    assert nonzero_count(0b11111111) == 8


def test_ones():
    assert ones(4) == 0b1111
    assert ones(8) == 0b11111111
    assert ones(1) == 0b1
    assert ones(0) == 0b0
    assert ones(10) == 0b1111111111


def test_one_hot():
    assert one_hot(4) == 0b10000
    assert one_hot(0) == 0b1
    assert one_hot(7) == 0b10000000
    assert one_hot(1) == 0b10


def test_ones_except():
    assert ones_except(4, 1) == 0b1101
    assert ones_except(4, 3) == 0b0111
    assert ones_except(8, 7) == 0b01111111
    assert ones_except(8, 0) == 0b11111110


def test_is_one_at():
    assert is_one_at(0b1101, 2) is True
    assert is_one_at(0b1101, 1) is False
    assert is_one_at(0b1000, 3) is True
    assert is_one_at(0b1111, 4) is False
    assert is_one_at(0b0, 0) is False
