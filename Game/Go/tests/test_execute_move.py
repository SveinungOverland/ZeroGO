from ..go import execute_move, VALID_MOVE, ERROR_KO
from .test_find_group import group_in_set

import numpy as np

def test_execute_move():
    board = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1],
    ])

    newBoard, status = execute_move(board, (2, 0, 2), history=[])
    assert status == VALID_MOVE
    assert not np.array_equal(board, newBoard)

    expected = np.array([
        [2, 2, 2, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1],
    ])

    assert np.array_equal(newBoard, expected)

def test_execute_move_with_capture():
    board = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1],
    ])

    newBoard, status = execute_move(board, (2, 1, 3), history=[])
    assert status == VALID_MOVE
    assert not np.array_equal(board, newBoard)

    expected = np.array([
        [2, 2, 0, 0],
        [2, 0, 2, 2],
        [2, 0, 0, 0],
        [0, 2, 0, 0],
    ])

    assert np.array_equal(newBoard, expected)

def test_execute_move_with_ko():
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 2, 0],
        [1, 2, 0, 2],
        [0, 1, 2, 0],
    ])

    history = np.array([
        [
            [0, 0, 0, 0],
            [0, 1, 2, 0],
            [1, 0, 1, 2],
            [0, 1, 2, 0],
        ],
        [
            [0, 0, 0, 0],
            [0, 1, 2, 0],
            [1, 2, 0, 2],
            [0, 1, 2, 0],
        ],
    ])

    newBoard, status = execute_move(board, (1, 2, 2), history=history)
    assert status == ERROR_KO
    assert np.array_equal(board, newBoard)

    expected = np.array([
        [0, 0, 0, 0],
        [0, 1, 2, 0],
        [1, 2, 0, 2],
        [0, 1, 2, 0],
    ])

    assert np.array_equal(newBoard, expected)
