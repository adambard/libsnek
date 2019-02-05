from libsnek import movement, data
from nose.tools import eq_

from .fixtures import RAW


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

def test_is_safe():
    bs = data.BoardState(RAW)

    assert movement.is_safe(bs, bs.other_snakes[0].body[2]) is False
    assert movement.is_safe(bs, (5, 6)) is True
    assert movement.is_safe(bs, (8, 5)) is False

def test_flood_fill():
    bs = data.BoardState(RAW)

    points = movement.flood_fill(bs, (8, 4))
    eq_(len(points), 135)


def test_find_path():
    bs = data.BoardState(RAW)

    points = movement.find_path(bs, (8, 4), (9, 6))
    eq_(points, [(7, 4), (7, 5), (7, 6), (8, 6), (9, 6)])

    eq_(points, movement.find_path_astar(bs, (8, 4), (9, 6)))

