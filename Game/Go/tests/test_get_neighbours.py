from ..go import get_neighbours
from .test_find_group import group_in_set

import numpy as np

def test_get_neighbours():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 1],
        [0, 0, 1, 0],
    ])

    group = get_neighbours(board, 2, 2)
    print(group)
    assert group_in_set(group, {
        (2, 1, 1),
        (2, 3, 1),
        (1, 2, 0),
        (3, 2, 1),
    })

def test_get_neighbours():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 1],
        [0, 0, 1, 0],
    ])

    group = get_neighbours(board, 2, 2, point_type=1)
    print(group)
    assert group_in_set(group, {
        (2, 1, 1),
        (2, 3, 1),
        (3, 2, 1),
    })
