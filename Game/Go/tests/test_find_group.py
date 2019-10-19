from ..go import find_group

import numpy as np

def test_find_group():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [2, 1, 1, 1],
        [2, 0, 1, 0],
    ])

    group = find_group(board, 2, 2)
    assert group_in_set(group, {
        (1, 1),
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 2),
    })

    group = find_group(board, 3, 3)
    assert group_in_set(group, {
        (3, 3)
    })

    group = find_group(board, 0, 0)
    assert group_in_set(group, {
        (0, 0),(0, 1),(0, 2),(0, 3),
        (1, 0),(1, 2), (1, 3),
    })

    group = find_group(board, 3, 0)
    assert group_in_set(group, {
        (2, 0),
        (3, 0)
    })



def group_in_set(group, expected):
    actual = {}
    for g in map(tuple, group):
        actual[g] = True
    for d in expected:
        if d not in actual:
            return False
    return True