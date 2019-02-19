from libsnek import data, movement
from nose.tools import eq_

from .fixtures import RAW


def test_board_state():
    bs = data.BoardState(RAW)

    eq_(bs.you.body, [(4, 2), (4, 3), (5, 3), (5, 4)])

    eq_(bs.you.head, (4, 2))

    eq_(bs.you.tail, (5, 4))

    eq_(bs.you.health, 63)

    eq_(bs.board_array[7, 7], 0)
    eq_(bs.board_array[5, 2], 1)


def test__as_snake__negative_head__doesnt_error():
    bs = data.BoardState(RAW)
    bs.as_snake(bs.you, (4, -1))


def test_as_snake():
    bs = data.BoardState(RAW)

    me = bs.you
    him = bs.other_snakes[0]

    new_board = bs.as_snake(him)
    yield eq_, bs.you.id, new_board.other_snakes[0].id
    yield eq_, bs.you.body, new_board.other_snakes[0].body

    my_move = movement.move(me.head, "u")

    new_board_with_move = bs.as_snake(him, with_move=my_move)

    yield eq_, my_move, new_board_with_move.other_snakes[0].head


