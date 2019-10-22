from ..go import capture_group
from .test_find_group import group_in_set

import numpy as np

def test_no_capture():
    board = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 2],
    ])

    was_captured = capture_group(board, np.array([[1, 1], [2, 1], [2, 2], [2, 3],[3, 2]]))
    assert not was_captured

    expected = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 2],
    ])
    assert np.array_equal(board, expected)

def test_capture():
    board = np.array([
        [0, 2, 0, 0],
        [2, 1, 2, 2],
        [2, 1, 1, 1],
        [0, 2, 1, 2],
    ])

    was_captured = capture_group(board, np.array([[1, 1], [2, 1], [2, 2], [2, 3],[3, 2]]))
    assert was_captured

    expected = np.array([
        [0, 2, 0, 0],
        [2, 0, 2, 2],
        [2, 0, 0, 0],
        [0, 2, 0, 2],
    ])
    assert np.array_equal(board, expected)