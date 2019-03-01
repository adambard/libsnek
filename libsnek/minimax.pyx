"""
A minimax layer that searches for significant outcomes (i.e. our death
or another snake's victory).
"""

import numpy as np
import functools

cimport libsnek.data as data
from movement import is_ok, surroundings, distance


MIN_SCORE = 0.001
MAX_SCORE = 9999
NEUTRAL_SCORE = 1
KILL_SCORE = 1.1


cdef bint c_is_dead(int[:, :] board, (int, int) pos):
    x, y = pos
    if x < 0 or y < 0:
        return True

    width, height = np.shape(board)
    if x >= width or y >= height:
        return True

    val = board[x, y]
    if val == data.YOU_BODY:
        return True
    elif val == data.SNAKE_BODY:
        return True

    return False


@functools.lru_cache(maxsize=128, typed=False)
def is_dead(board_state, pos=None):
    if pos is None:
        pos = board_state.you.head

    if board_state.you.health <= 1:
        # TODO Calculate nearest food and use this
        return True

    elif c_is_dead(board_state.board_array, pos):
        return True

    else:
        for s in board_state.other_snakes:
            if pos == s.tail:
                return any(p in board_state.food for p in surroundings(s.head))
            elif pos == s.head:
                return len(s.body) >= len(board_state.you.body)

    return False


def score_board_state(board_state):
    """
    If we've died, return MIN_SCORE
    If we've won, return MAX_SCORE
    Otherwise, return 0
    """
    if is_dead(board_state):
        return MIN_SCORE

    all_others_dead = True
    num_dead = 0
    for s in board_state.other_snakes:
        bs = board_state.as_snake(s)
        if is_dead(bs):
            num_dead += 1
        else:
            all_others_dead = False

    if all_others_dead:
        return MAX_SCORE

    if all(is_dead(board_state, p) for p in surroundings(board_state.you.head)):
        # We are trapped
        return MIN_SCORE

    if num_dead > 0:
        return KILL_SCORE ** num_dead
    else:
        return NEUTRAL_SCORE


def minimax_nodes(board_state):
    """Return a set of board states representing moves in each valid direction"""

    return [
        board_state.as_snake(board_state.you, with_move=pos)
        for pos in surroundings(board_state.you.head)
        if not c_is_dead(board_state.board_array, pos)
    ]


cdef double combine_snake_scores(list scores):
    """
    Normally, minimax would use the minimum score.
    We'll do the same, but bump it up for any more-than-minimum
    scores we find -- better a possible death than a certain one.
    """
    # Scores is an array of MIN_SCORE, MAX_SCORe, or NEUTRAL_SSCORE
    if not scores:
        return 1.0  # NEUTRAL_SCORE

    cdef double min_score, bonus
    min_score = 9999.0
    bonus = 0.0
    for s in scores:
        if s < min_score:
            min_score = s

        if s >= 1.0:
            # We did ok, add an extra min score
            bonus += 0.01

    return min_score + bonus


def minimax_score(board_state, maximizing_player=True, depth=5):

    if maximizing_player:

        # Only conclude minimax before our turn (since we start with a move)
        board_score = score_board_state(board_state)

        if board_score == MIN_SCORE or board_score == MAX_SCORE or depth <= 0:
            if board_score == MIN_SCORE:
                # Make sure that a far-future death is worth more than
                # an impending one.
                return board_score * (9 - depth)
            return board_score

        # Make our own best move
        max_score = MIN_SCORE
        for bs in minimax_nodes(board_state):
            max_score = max(max_score, minimax_score(bs, False, depth - 1))

        return max_score

    else:
        # Make each other snake's move to minimize our score
        scores = []

        new_bs = board_state

        for s in board_state.other_snakes:
            if distance(board_state.you.head, s.head) > depth:
                # A snake more than <depth> away can't reach us, save
                # a little time by skipping their move
                continue

            snake_scores = [MAX_SCORE]
            min_score = MAX_SCORE

            for bs in minimax_nodes(new_bs.as_snake(s)):
                score = minimax_score(bs.as_snake(board_state.you), True, depth - 1)
                snake_scores.append(score)
                if score < min_score:
                    min_score = score
                    new_bs = bs

            scores.append(combine_snake_scores(snake_scores))

        if not scores:
            return minimax_score(board_state, True, depth - 1)

        return min(scores)


def apply(board_state, depth=5):
    positions = surroundings(board_state.you.head)

    out = []

    for pos in positions:
        if is_dead(board_state, pos):
            out.append(MIN_SCORE)
        else:
            bs = board_state.as_snake(board_state.you, with_move=pos)
            out.append(minimax_score(bs, False, depth=depth))

    return np.array(out)

