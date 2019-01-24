from typing import List
import numpy as np

def normalize_max(nums: List) -> List[float]:
    """
    Given a list of numbers, return a new list of numbers such that
    1 is the maximum value
    """
    maxval = max(nums)
    if maxval == 0:
        return [0. for _ in nums]
    return [float(n) / maxval for n in nums]


def normalize_min(nums: List):
    return [1.0 - n for n in normalize_max(nums)]


def rms(vals):
    return np.sqrt(np.mean(np.array(vals)))

