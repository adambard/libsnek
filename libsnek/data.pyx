import functools
import numpy as np

from typing import List, Tuple

from libc.stdlib cimport malloc, free


cdef (int, int) point_to_tuple(dict p):
    return (p["x"], p["y"])


cdef class Snake(object):
    cdef dict raw

    def __init__(self, raw_snake):
        self.raw = raw_snake

    @property
    def id(self):
        return self.raw["id"]

    @property
    def name(self):
        return self.raw["name"]

    @property
    def health(self):
        return self.raw["health"]

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
    cdef int[:, :] _board
    cdef dict raw

    def __init__(self, raw_board_state):
        self.raw = raw_board_state

        self.init_board()

    def init_board(self):
        self._board = np.zeros((self.width, self.height), dtype=np.intc)

        for (x, y) in self.food:
            self._board[x, y] = FOOD

        x, y = self.you.head
        self._board[x, y] = YOU_HEAD

        x, y = self.you.tail
        self._board[x, y] = YOU_TAIL

        for x, y in self.you.body[1:-1]:
            self._board[x, y] = YOU_BODY

        for s in self.other_snakes:
            x, y = s.head
            self._board[x, y] = SNAKE_HEAD

            x, y = s.tail
            self._board[x, y] = SNAKE_TAIL

            for x, y in s.body[1:-1]:
                self._board[x, y] = SNAKE_BODY

    def __eq__(self, other):
        return other.id == self.id and other.turn == self.turn and other.you.id == self.you.id

    def __hash__(self):
        return hash((self.id, self.turn, self.you.id))

    @functools.lru_cache(maxsize=8, typed=False)
    def as_snake(self, other: Snake, with_move=None):
        if with_move is not None:
            x, y = with_move
            # Simulate a move by <you>, whoever that is at the moment
            snakes = self.raw["board"]["snakes"]

            snakes = [
                dict(s, body=[{"x": x, "y": y}] + s["body"][:-1]) if s["id"] == self.you.id else s
                for s in snakes
            ]

            board = dict(self.raw["board"], snakes=snakes)
            return BoardState(dict(self.raw, you=other.raw, board=board))

        return BoardState(dict(self.raw, you=other.raw))

    @property
    def board_array(self):
        return self._board

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
        return [s for s in self.snakes if s.id != self.you.id]
