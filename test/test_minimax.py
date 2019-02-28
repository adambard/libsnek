import uuid

from .fixtures import RAW, RAW_DANGER
import numpy as np

from nose.tools import eq_
from libsnek import data, minimax
from libsnek.movement import is_ok


def snake(body, health=100):
    return {
        "id": uuid.uuid4(),
        "health": health,
        "body": [
            {"x": x, "y": y} for x, y in body
        ]
    }


TRAP_YOU = {
    "id": uuid.uuid4(),
    "health": 100,
    "body": [
        {"x": 4, "y": 1},
        {"x": 3, "y": 1},
        {"x": 2, "y": 1},
        {"x": 1, "y": 1},
        {"x": 1, "y": 2},
    ]
}

TRAP_BOARD = {
    "you": TRAP_YOU,
    "turn": 7,
    "board": {
        "width": 12,
        "height": 12,
        "food": [
            {"x": 2, "y": 4},
            {"x": 5, "y": 2},
            {"x": 5, "y": 6},
        ],
        "snakes": [
            {
                "id": str(uuid.uuid4()),
                "health": 98,
                "name": "Bob-jim",
                "body": [
                    {"x": 3, "y": 0},
                    {"x": 2, "y": 0},
                    {"x": 1, "y": 0},
                    {"x": 0, "y": 0},
                    {"x": 0, "y": 1},
                    {"x": 0, "y": 2},
                    {"x": 0, "y": 3},
                    ]
                },
            TRAP_YOU 
        ]
    },
    "game": {
        "id": str(uuid.uuid4()),
    },
}


def test_trap_minimax():
    """
    Test Trap minimax
    [[6 6 6 5 0 0 0 0 0 0 0 0]
     [6 3 3 3 2 0 0 0 0 0 0 0]
     [6 4 0 0 0 1 0 0 0 0 0 0]
     [7 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 1 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 1 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]]
    """
    bs = data.BoardState(TRAP_BOARD)

    scores = minimax.apply(bs, depth=3)

    yield eq_, list(scores), [minimax.MIN_SCORE, minimax.NEUTRAL_SCORE, minimax.NEUTRAL_SCORE, minimax.MIN_SCORE]

    TRAP_BOARD["you"] = TRAP_BOARD["board"]["snakes"][1] = dict(TRAP_YOU, body=[{"x": 5, "y": 1}] + TRAP_YOU["body"])
    bs = data.BoardState(TRAP_BOARD)
    scores = minimax.apply(bs, depth=3)

    yield eq_, list(scores), [minimax.MAX_SCORE, minimax.NEUTRAL_SCORE, minimax.NEUTRAL_SCORE, minimax.MIN_SCORE]


DOOMED_YOU = {
    "id": uuid.uuid4(),
    "health": 100,
    "body": [
        {"x": 1, "y": 1},
        {"x": 1, "y": 2},
        {"x": 1, "y": 3},
    ]
}

DOOMED_BOARD = {
    "you": DOOMED_YOU,
    "turn": 7,
    "board": {
        "width": 12,
        "height": 12,
        "food": [
            {"x": 2, "y": 4},
            {"x": 5, "y": 2},
            {"x": 5, "y": 6},
        ],
        "snakes": [
            {
                "id": str(uuid.uuid4()),
                "health": 98,
                "name": "Bob-jim",
                "body": [
                    {"x": 2, "y": 2},
                    {"x": 2, "y": 1},
                    {"x": 2, "y": 0},
                    {"x": 1, "y": 0},
                    {"x": 0, "y": 0},
                    {"x": 0, "y": 1},
                    {"x": 0, "y": 2},
                    {"x": 0, "y": 3},
                    ]
                },
            DOOMED_YOU 
        ]
    },
    "game": {
        "id": str(uuid.uuid4()),
    },
}

def test_impending_doom():
    """
    [[6 6 6 0 0 0 0 0 0 0 0 0]
     [6 2 6 0 0 0 0 0 0 0 0 0]
     [6 3 5 0 0 1 0 0 0 0 0 0]
     [7 4 0 0 0 0 0 0 0 0 0 0]
     [0 0 1 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 1 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]
     [0 0 0 0 0 0 0 0 0 0 0 0]]
    """

    bs = data.BoardState(DOOMED_BOARD)

    assert not is_ok(bs, (0, 1))
    assert not is_ok(bs, (1, 0))
    assert not is_ok(bs, (2, 1))
    assert not is_ok(bs, (1, 2))
    eq_(minimax.score_board_state(bs), minimax.MIN_SCORE)



def test_minimax():
    bs = data.BoardState(RAW_DANGER)
    #eq_(minimax.minimax_score(bs), minimax.NEUTRAL_SCORE)

    assert (4, 1) in bs.other_snakes[0].body
    up_board = bs.as_snake(bs.you, (4, 1))

    assert minimax.is_dead(up_board)
    eq_(minimax.score_board_state(bs.as_snake(bs.you, with_move=(4, 1))), minimax.MIN_SCORE)

    scores = minimax.apply(bs, depth=2)
    expected_scores = np.array([minimax.MIN_SCORE, minimax.MIN_SCORE, minimax.MIN_SCORE, minimax.NEUTRAL_SCORE])

    eq_(list(scores), list(expected_scores))


SIT_YOU = snake([
    (8, 9),
    (8, 8),
    (8, 7),
    (7, 7),
    (7, 6),
    (8, 6),
    (8, 5),
    (8, 4),
    (8, 3),
    (8, 2),
    (7, 2),
    (7, 1),
])

SIT_BOARD = {
    "you": SIT_YOU,
    "turn": 118,
    "game": {
        "id": str(uuid.uuid4()),
    },
    "board": {
        "width": 11,
        "height": 11,
        "food": [
            {"x": 7, "y": 10},
            {"x": 0, "y": 9},
            {"x": 3, "y": 3},
            {"x": 10, "y": 0},
        ],
        "snakes": [
            snake([
                (7, 9),
                (6, 9),
                (6, 8),
                (5, 8),
                (5, 7),
                (6, 7),
                (6, 6),
                (5, 6),
                (4, 6),
            ]),
            SIT_YOU
        ]
    }
}

def test_situation():
    bs = data.BoardState(SIT_BOARD)
    scores = minimax.apply(bs, depth=3)
    eq_(list(scores), [minimax.MIN_SCORE, minimax.NEUTRAL_SCORE, minimax.NEUTRAL_SCORE, minimax.MIN_SCORE])

