# distutils: language=c++

import functools
import queue
from typing import Tuple
import numpy as np

from libc.math cimport sqrt
from libcpp.queue cimport queue as cqueue

cimport libsnek.data as data
from .data import BoardState

cdef enum Dir:
    DIR_U, DIR_R, DIR_D, DIR_L


cdef (int, int) cmove((int, int) pos, Dir d):
    x, y = pos
    if d == DIR_U:
        return (x, y - 1)
    elif d == DIR_R:
        return (x + 1, y)
    elif d == DIR_D:
        return (x, y + 1)
    elif d == DIR_L:
        return (x - 1, y)


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


cdef ((int, int), (int, int), (int, int), (int, int)) csurroundings((int, int) pos):
    return (
        cmove(pos, DIR_U),
        cmove(pos, DIR_R),
        cmove(pos, DIR_D),
        cmove(pos, DIR_L),
    )


def surroundings(pos):
    """
    Return a list of the result of moving up, right, down, and left
    from the provided point (in that order)
    """
    return csurroundings(pos)


def distance_abs(pos1, pos2):
    """
    Return the absolute distance between two points
    """

    x1, y1 = pos1
    x2, y2 = pos2

    return sqrt((x1 - x2)**2.0 + (y1 - y2)**2.0)


cdef int cdistance((int, int) pos1, (int, int) pos2):
    x1, y1 = pos1
    x2, y2 = pos2

    return abs(x1 - x2) + abs(y1 - y2)

def distance(pos1, pos2):
    """Manhattan distance between two points"""
    return cdistance(pos1, pos2)


cdef bint c_is_safe(int[:, :] board, (int, int) pos, int depth=1, int max_depth=2, bint check_edibility=True):
    cdef int x, y, x2, y2

    x, y = pos
    width, height = np.shape(board)

    if x < 0:
        return False
    elif x >= width:
        return False
    elif y < 0:
        return False
    elif y >= height:
        return False

    val = board[x, y]

    if val == data.YOU_BODY:
        return False
    elif val == data.YOU_HEAD:
        return False
    elif val == data.SNAKE_BODY:
        return False
    elif val == data.SNAKE_HEAD:
        return False
    elif val == data.SNAKE_TAIL:
        # The tail is safe, *unless* this snake is about to eat
        for x2, y2 in csurroundings(pos):
            if x2 < 0 or x2 >= width or y2 < 0 or y2 >= height:
                continue
            if board[x2, y2] == data.FOOD:
                return False

    # Snake head surroundings are considered unsafe for now (TODO consider other snake size)
    for x2, y2 in csurroundings(pos):
        if x2 < 0 or x2 >= width or y2 < 0 or y2 >= height:
            continue
        if board[x2, y2] == data.SNAKE_HEAD:
            return False

    if depth >= max_depth:
        return True
    else:
        for p in csurroundings(pos):
            if c_is_safe(board,
                       p,
                       depth + 1,
                       max_depth=max_depth,
                       check_edibility=check_edibility):
                return True

        return False


@functools.lru_cache(maxsize=128, typed=False)
def is_safe(board_state: BoardState, pos, depth=1, max_depth=2,
            check_edibility=True):

    return c_is_safe(board_state.board_array, pos, depth=depth, max_depth=max_depth, check_edibility=check_edibility)


@functools.lru_cache(maxsize=128, typed=False)
def flood_fill(board_state, start_pos, threshold=None, pred=None):
    """
    Returns a set of points constituting a flood fill from (start_pos)

    :param threshold: If threshold is provided, stop after we've visited that many points.
    :param pred: If a predicate is provided, use this instead of is_safe
    """

    pred = pred or functools.partial(is_safe, max_depth=1)

    if not pred(board_state, start_pos):
        return set()

    visited = set()

    cdef cqueue[(int, int)] frontier

    frontier.push(start_pos)

    while not frontier.empty():
        node = frontier.front()
        frontier.pop()

        if node in visited:
            continue

        visited.add(node)
        for p in csurroundings(node):
            if p not in visited and pred(board_state, p):
                frontier.push(p)

        if threshold and len(visited) >= threshold:
            return visited

    return visited



def find_path_pred(board_state, start_pos, end_pred):
    """
    Use breadth-first search to find the first point for which end_pred
    returns true, then return the path.  Returns None if no path was found.

    Many thanks to https://www.redblobgames.com/pathfinding/a-star/introduction.html
    """

    cdef cqueue[(int, int)] frontier
    frontier.push(start_pos)

    path = {start_pos: None}

    while not frontier.empty():
        pos = frontier.front()
        frontier.pop()

        if end_pred(pos):
            # Found it! Now work backwards to get the distance

            output = []

            while pos != start_pos and pos is not None:
                output.append(pos)
                pos = path[pos]

            return list(reversed(output))

        for next_pos in csurroundings(pos):
            if next_pos not in path and is_safe(board_state, next_pos, max_depth=1):
                frontier.push(next_pos)
                path[next_pos] = pos

    # Could not find a matching point
    return None


cdef list c_find_path(int[:, :] board, (int, int) start_pos, (int, int) end_pos):
    # Use breadth-first search to find the shortest path to a particular point
    # TODO: use A* instead (Need a priority queue)

    cdef (int, int) pos
    cdef dict path = {start_pos: None}
    cdef cqueue[(int, int)] frontier
    frontier.push(start_pos)

    while not frontier.empty():
        pos = frontier.front()
        frontier.pop()

        if pos == end_pos:
            output = []
            while pos != start_pos and pos is not None:
                output.append(pos)
                pos = path[pos]

            return list(reversed(output))

        for next_pos in csurroundings(pos):
            if next_pos in path:
                continue

            if not c_is_safe(board, next_pos, 1, max_depth=1):
                continue

            frontier.push(next_pos)
            path[next_pos] = pos

    return None


def find_path(board_state, start_pos, end_pos):
    return c_find_path(board_state.board_array, start_pos, end_pos)


def find_path_astar(board_state, start_pos, end_pos):
    # Use A* to find the shortest path to a particular point

    frontier = queue.PriorityQueue()
    frontier.put(start_pos, 0)
    path = {start_pos: None}
    cost = {start_pos: 0}

    while not frontier.empty():
        pos = frontier.get()

        if pos == end_pos:
            output = []

            while pos != start_pos and pos is not None:
                output.append(pos)
                pos = path[pos]

            return list(reversed(output))

        for next_pos in csurroundings(pos):
            if not is_safe(board_state, next_pos, max_depth=1):
                continue

            new_cost = cost[pos] + 1
            if next_pos not in cost or new_cost < cost[next_pos]:
                cost[next_pos] = new_cost
                path[next_pos] = pos
                priority = distance(end_pos, next_pos)
                frontier.put(next_pos, priority)

    return None

