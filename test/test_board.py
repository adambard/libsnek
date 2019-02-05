from libsnek import data
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
