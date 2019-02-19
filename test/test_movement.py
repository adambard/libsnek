import time
from libsnek import movement, data
from nose.tools import eq_

from .fixtures import RAW, RAW_DANGER


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
    assert movement.is_safe(bs, (10, 1)) is False
    assert movement.is_safe(bs, (11, 1)) is True
    assert movement.is_safe(bs, (12, 5)) is False
    assert movement.is_safe(bs, (11, 5)) is True

def test_flood_fill():
    bs = data.BoardState(RAW)

    points = movement.flood_fill(bs, (8, 4))
    eq_(len(points), 135)


def test_find_path():
    bs = data.BoardState(RAW)

    points = movement.find_path(bs, (8, 4), (9, 6))
    eq_(points, [(7, 4), (7, 5), (7, 6), (8, 6), (9, 6)])

    eq_(points, movement.find_path_astar(bs, (8, 4), (9, 6)))


def test_benchmark_find_path():
    bs = data.BoardState(RAW)

    N = 1000

    start_time = time.time()
    for _ in range(N):
        movement.find_path(bs, (4, 4), (11, 11))

    print("Find path:", time.time() - start_time)

    start_time = time.time()
    for _ in range(N):
        movement.find_path_astar(bs, (4, 4), (11, 11))
    print("Find path astar:", time.time() - start_time)


def test_flood_fill_with_swapped_board():
    bs = data.BoardState(RAW)

    him = bs.other_snakes[0]

    new_board = bs.as_snake(him)
    visited = movement.flood_fill(new_board, him.head, threshold=10)
    yield eq_, len(visited), 10


def test_flood_fill_own_head_danger_if_not_start():
    bs = data.BoardState(RAW_DANGER)

    visited = movement.flood_fill(bs, (5, 2))
    yield eq_, len(visited), 1
