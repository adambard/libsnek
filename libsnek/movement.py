import functools
import queue
from typing import Tuple
from math import sqrt

from .data import BoardState


def move(pos: Tuple[int, int], d):
    """
    Given a position and a direction, return a new position.

    Board size is not known, so that's your problem
    """
    x, y = pos
    if d == "u":
        return (x, y - 1)
    elif d == "r":
        return (x + 1, y)
    elif d == "d":
        return (x, y + 1)
    elif d == "l":
        return (x - 1, y)
    else:
        return pos


def surroundings(pos):
    """
    Return a list of the result of moving up, right, down, and left
    from the provided point (in that order)
    """
    return [
        move(pos, "u"),
        move(pos, "r"),
        move(pos, "d"),
        move(pos, "l"),
    ]


def distance_abs(pos1, pos2):
    """
    Return the absolute distance between two points
    """

    x1, y1 = pos1
    x2, y2 = pos2

    return sqrt((x1 - x2)**2.0 + (y1 - y2)**2.0)


def distance(pos1, pos2):
    """Manhattan distance between two points"""
    x1, y1 = pos1
    x2, y2 = pos2

    return abs(x1 - x2) + abs(y1 - y2)


@functools.lru_cache(maxsize=128, typed=False)
def is_safe(board_state: BoardState, pos, depth=1, max_depth=2,
            check_edibility=True):
    x, y = pos

    if x < 0:
        return False
    elif x >= board_state.width:
        return False
    elif y < 0:
        return False
    elif y >= board_state.height:
        return False

    for snake in board_state.snakes:
        # Heads and tails are handled specially later
        if pos in snake.body[:-1]:
            return False

        # The tail is safe, *unless* this snake is about to eat
        tail = snake.body[:-1]
        if pos == tail:
            head = snake.body[0]
            for p in surroundings(head):
                if p in  board_state.food:
                    return False

        if check_edibility and snake.id != board_state.you.id:
            # The area around another snake's head is safe, if
            # that snake is shorter than us (and is not us)
            if len(snake) >= len(board_state.you):
                if pos in surroundings(snake.body[0]):
                    return False


    if depth >= max_depth:
        return True

    else:
        return any(
            is_safe(
                board_state,
                p,
                depth=depth + 1,
                max_depth=max_depth,
                check_edibility=check_edibility
            ) for p in surroundings(pos)
        )


@functools.lru_cache(maxsize=128, typed=False)
def flood_fill(board_state, start_pos, threshold=None):
    """
    Returns a set of points constituting a flood fill from (start_pos)

    If threshold is provided, stop after we've visited that many points.
    """
    if not is_safe(board_state, start_pos, max_depth=1):
        return set()

    visited = {start_pos}
    frontier = queue.Queue()
    frontier.put(start_pos)

    while not frontier.empty():
        node = frontier.get()
        visited.add(node)
        for p in surroundings(node):
            if p not in visited and is_safe(board_state, p):
                frontier.put(p)

        if threshold and len(visited) >= threshold:
            return visited

    return visited



def find_path_pred(board_state, start_pos, end_pred):
    """
    Use breadth-first search to find the first point for which end_pred
    returns true, then return the path.  Returns None if no path was found.

    Many thanks to https://www.redblobgames.com/pathfinding/a-star/introduction.html
    """

    frontier = queue.Queue()
    frontier.put(start_pos)

    path = {start_pos: None}

    while not frontier.empty():
        pos = frontier.get()
        if end_pred(pos):
            # Found it! Now work backwards to get the distance

            output = []

            while pos != start_pos and pos is not None:
                output.append(pos)
                pos = path[pos]

            return list(reversed(output))

        for next_pos in surroundings(pos):
            if next_pos not in path and is_safe(board_state, next_pos, max_depth=1):
                frontier.put(next_pos)
                path[next_pos] = pos

    # Could not find a matching point
    return None



def find_path(board_state, start_pos, end_pos):
    # Use A* to find the shortest path to a particular point

    frontier = queue.PriorityQueue()
    frontier.put(start_pos, 0)
    path = {start_pos: None}
    cost = {start_pos: 0}

    while not frontier.empty():
        pos = frontier.get()
        if pos == end_pos:
            path = []

            while pos != start_pos and pos is not None:
                path.append(pos)
                pos = path[pos]

            return reversed(path)

        neighbours = [p for p in surroundings(pos) if is_safe(board_state, p)]

        for next_pos in neighbours:
            new_cost = cost[pos] + 1
            if next_pos not in cost or new_cost < cost[next_pos]:
                cost[next_pos] = new_cost
                path[next_pos] = pos
                priority = distance(end_pos, next_pos)
                frontier.put(next_pos, priority)

    return None

