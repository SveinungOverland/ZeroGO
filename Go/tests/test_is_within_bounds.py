from ..go import is_within_bounds
import numpy as np

def test_valid_bounds():
    board = np.ndarray((5,5))
    assert is_within_bounds(board, 4, 4)
    assert is_within_bounds(board, 0, 0)
    assert is_within_bounds(board, 3, 2)
    assert is_within_bounds(board, 2, 3)
    assert is_within_bounds(board, 2, 2)

def test_not_valid_bounds():
    board = np.ndarray((5,5))
    assert is_within_bounds(board, -1, 0)
    assert is_within_bounds(board, 0, -1)
    assert is_within_bounds(board, 4, 5)
    assert is_within_bounds(board, 5, 4)
    assert is_within_bounds(board, 5, 5)