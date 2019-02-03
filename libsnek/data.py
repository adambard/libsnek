import functools


def point_to_tuple(p):
    return (p["x"], p["y"])


class Snake(object):
    def __init__(self, raw_snake):
        self.raw = raw_snake

    @property
    def id(self):
        return self.raw["id"]

    @property
    def health(self):
        return self.raw["health"]

    @property
    def name(self):
        return self.raw["name"]

    @property
    def body(self):
        return [point_to_tuple(p) for p in self.raw["body"]]

    @property
    def head(self):
        return self.body[0]

    @property
    def tail(self):
        return self.body[-1]

    def __len__(self):
        return len(self.body)


class BoardState(object):

    def __init__(self, raw_board_state):
        self.raw = raw_board_state

    def __eq__(self, other):
        return other.id == self.id and other.turn == self.turn and other.you.id == self.you.id

    def __hash__(self):
        return hash((self.id, self.turn, self.you.id))

    @functools.lru_cache(maxsize=8, typed=False)
    def as_snake(self, other: Snake):
        return BoardState(dict(self.raw, you=[{"x": x, "y": y} for x, y in other.body]))

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
