from .fixtures import RAW_DANGER
import numpy as np

from nose.tools import eq_
from libsnek import data, minimax

def test_minimax():
    bs = data.BoardState(RAW_DANGER)
    #eq_(minimax.minimax_score(bs), minimax.NEUTRAL_SCORE)

    assert (4, 1) in bs.other_snakes[0].body
    up_board = bs.as_snake(bs.you, (4, 1))

    assert minimax.is_dead(up_board)
    eq_(minimax.score_board_state(bs.as_snake(bs.you, with_move=(4, 1))), minimax.MIN_SCORE)

    scores = minimax.apply(bs)
    expected_scores = np.array([minimax.MIN_SCORE, minimax.MIN_SCORE, minimax.MIN_SCORE, minimax.NEUTRAL_SCORE])

    eq_(list(scores), list(expected_scores))

