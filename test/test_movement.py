from libsnek import movement
from nose.tools import eq_


def test_move():
    eq_(
        movement.move((1, 2), "u"),
        (1, 1)
    )


def test_surroundings():
    eq_(
        movement.surroundings((1, 2)),
        ((1, 1), (2, 2), (1, 3), (0, 2))
    )


def test_distance():
    eq_(
        movement.distance((1, 1), (3, 3)),
        4
    )
