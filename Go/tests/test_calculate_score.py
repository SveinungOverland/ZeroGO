from ..go import calculate_score

import numpy as np

def test_calculate_score():
    board = np.array([
        [0, 1, 0, 1, 0],
        [1, 1, 1, 0, 1],
        [2, 2, 1, 1, 0],
        [0, 2, 2, 0, 0],
        [0, 2, 2, 2, 2],
    ])

    black_score, white_score, score_board = calculate_score(board)

    assert black_score == 12
    assert white_score == 10
    assert np.array_equal(score_board, 
    np.array([
        [1, 0, 1, 0 ,1],
        [0, 0, 0, 1, 0],
        [0 ,0 ,0 ,0 ,0],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
    ]))

def test_calculate_score_2():
    board = np.array([
        [0, 2, 0, 0, 0],
        [1, 2, 0, 0, 0],
        [0, 1, 2, 2, 0],
        [0, 1, 1, 1, 2],
        [0, 0, 0, 0, 0]
    ])

    black_score, white_score, score_board = calculate_score(board)

    assert black_score == 5
    assert white_score == 12
    assert np.array_equal(score_board, 
    np.array([
        [0, 0, 2, 2, 2],
        [0, 0, 2, 2, 2],
        [0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]))
