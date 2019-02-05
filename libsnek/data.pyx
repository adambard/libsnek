import functools
import numpy as np
from typing import List, Tuple


cdef (int, int) point_to_tuple(dict p):
    return (p["x"], p["y"])


cdef class Snake(object):
    cdef long[:, :] _body
    cdef int _health
    cdef dict raw

    def __init__(self, raw_snake):
        self.raw = raw_snake

        self._health = raw_snake["health"]
        self._body = np.array([
            point_to_tuple(p) for p in self.raw["body"]
        ])

    @property
    def id(self):
        return self.raw["id"]

    @property
    def name(self):
        return self.raw["name"]

    @property
    def health(self):
        return self._health

    @property
    def cbody(self):
        return self._body

    @property
    def chead(self):
        return self.cbody[0, :]

    @property
    def ctail(self):
        return self.cbody[-1, :]

    @property
    def body(self) -> List[Tuple[int, int]]:
        return [point_to_tuple(p) for p in self.raw["body"]]

    @property
    def head(self):
        return self.body[0]

    @property
    def tail(self):
        return self.body[-1]

    def __len__(self):
        return len(self.body)


cdef class BoardState(object):
    cdef dict raw

    def __init__(self, raw_board_state):
        self.raw = raw_board_state

    def __eq__(self, other):
        return other.id == self.id and other.turn == self.turn and other.you.id == self.you.id

    def __hash__(self):
        return hash((self.id, self.turn, self.you.id))

    @functools.lru_cache(maxsize=8, typed=False)
    def as_snake(self, other: Snake):
        return BoardState(dict(self.raw, you=other.raw))

    @property
    def id(self):
        return self.raw["game"]["id"]

    @property
    def turn(self):
        return self.raw["turn"]

    @property
    def you(self):
        return Snake(self.raw["you"])

    @property
    def width(self):
        return self.raw["board"]["width"]

    @property
    def height(self):
        return self.raw["board"]["height"]

    @property
    def food(self):
        return {point_to_tuple(p) for p in self.raw["board"]["food"]}

    @property
    def snakes(self):
        return [Snake(p) for p in self.raw["board"]["snakes"]]

    @property
    def other_snakes(self):
        return [s for s in self.snakes if s.head != self.you.head]
