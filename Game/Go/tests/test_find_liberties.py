from ..go import find_liberties
from .test_find_group import group_in_set

import numpy as np

def test_find_liberties():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 1],
        [0, 0, 1, 0],
    ])

    liberties = find_liberties(board,  np.array([[1, 1], [2, 1], [2, 2], [2, 3],[3, 2]]))
    print(liberties)
    assert group_in_set(liberties, {
        (0, 1),
        (1, 0), (1, 2), (1, 3),
        (2, 0),
        (3, 1), (3, 3)
    })

def test_find_liberties_2():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 2, 2],
        [0, 1, 1, 1],
        [0, 0, 1, 0],
    ])

    liberties = find_liberties(board,  np.array([[1,2], [1, 3]]))
    print(liberties)
    assert group_in_set(liberties, {
        (0, 2), (0, 3),
        (1, 1),
        (2, 2), (2, 3)
    })