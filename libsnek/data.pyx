import uuid
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


cdef void setVal(int[:, :] board, (int, int) point, PosState val):
    cdef int width, height
    cdef int x, y

    x, y = point

    if x < 0 or y < 0:
        return

    width, height = np.shape(board)

    if x >= width or y >= height:
        return

    board[x, y] = val



cdef class BoardState(object):
    cdef int[:, :] _board
    cdef dict raw

    def __init__(self, raw_board_state):
        self.raw = raw_board_state

        self.init_board()

    def init_board(self):
        self._board = np.zeros((self.width, self.height), dtype=np.intc)

        for pos in self.food:
            setVal(self._board, pos, FOOD)

        setVal(self._board, self.you.head, YOU_HEAD)
        setVal(self._board, self.you.tail, YOU_TAIL)

        for p in self.you.body[1:-1]:
            setVal(self._board, p, YOU_BODY)

        for s in self.other_snakes:
            setVal(self._board, s.head, SNAKE_HEAD)
            setVal(self._board, s.tail, SNAKE_TAIL)

            for pos in s.body[1:-1]:
                setVal(self._board, pos, SNAKE_BODY)

    def __eq__(self, other):
        return other.id == self.id and other.turn == self.turn and other.you.id == self.you.id

    def __hash__(self):
        return hash((self.id, self.turn, self.you.head))

    @functools.lru_cache(maxsize=8, typed=False)
    def as_snake(self, other: Snake, with_move=None):
        if with_move is not None:
            x, y = with_move
            # Simulate a move by <you>, whoever that is at the moment
            snakes = self.raw["board"]["snakes"]

            if with_move in self.food:
                new_body = [{"x": x, "y": y}] + self.raw["you"]["body"]
                new_health = 100
            else:
                new_body = [{"x": x, "y": y}] + self.raw["you"]["body"][:-1]
                new_health = self.you.health - 1

            snakes = [
                dict(s, body=new_body, health=new_health) if s["id"] == self.you.id else s
                for s in snakes
            ]

            you = [s for s in snakes if s["id"] == other.id][0]
            game = dict(self.raw["game"], id=str(uuid.uuid4()))
            board = dict(self.raw["board"], snakes=snakes)
            return BoardState(dict(self.raw, you=you, board=board, game=game))

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
