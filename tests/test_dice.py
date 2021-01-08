import pytest

from app.utils.dice import roll


def test_roll_d4():
    total = 0
    rolls = 0
    for i in range(1000):
        r = roll('d4')
        assert r >= 1
        assert r <= 4

        total += r
        rolls += 1

    assert abs((total / rolls) - 2.5) < .1


def test_roll_d6():
    total = 0
    rolls = 0
    for i in range(1000):
        r = roll('d6')
        assert r >= 1
        assert r <= 6

        total += r
        rolls += 1

    assert abs((total / rolls) - 3.5) < .1


def test_roll_3d6():
    total = 0
    rolls = 0
    for i in range(1000):
        r = roll('3d6')
        assert r >= 3
        assert r <= 18

        total += r
        rolls += 1

    assert abs((total / rolls) - 10.5) < .1
