import uuid
from libsnek import data
from nose.tools import eq_
import numpy as np

def test_board_state():
    raw_you = {
            "id": str(uuid.uuid4()),
            "health": 63,
            "name": "Jim-bob",
            "body": [
                {"x": 4, "y": 2},
                {"x": 4, "y": 3},
                {"x": 5, "y": 3},
                {"x": 5, "y": 4}
                ]
            }
    raw = {
        "you": raw_you,
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
                        {"x": 9, "y": 1},
                        {"x": 9, "y": 2},
                        {"x": 9, "y": 3},
                        {"x": 9, "y": 4},
                        {"x": 9, "y": 5},
                        {"x": 8, "y": 5},
                    ]
                },
                raw_you
            ]
        },
        "game": {
            "id": str(uuid.uuid4()),
        },
    }

    bs = data.BoardState(raw)

    eq_(bs.you.body, [(4, 2), (4, 3), (5, 3), (5, 4)])
    assert np.all(bs.you.cbody == np.array([(4, 2), (4, 3), (5, 3), (5, 4)]))

    eq_(bs.you.head, (4, 2))
    assert np.all(bs.you.chead == np.array([4, 2]))

    eq_(bs.you.tail, (5, 4))
    assert np.all(bs.you.ctail == np.array([5, 4]))

    eq_(bs.you.health, 63)
