from ..go import all_possible_moves, BLACK, WHITE

import numpy as np

def test_all_possible_moves():
    player = BLACK
    state = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1]
    ])

    expected_1 = np.array([
        [2, 2, 1, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1]
    ])

    expected_2 = np.array([
        [2, 2, 0, 1],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [0, 2, 1, 1]
    ])

    expected_3 = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 1],
        [2, 1, 1, 1],
        [0, 2, 1, 1]
    ])

    expected_4 = np.array([
        [2, 2, 0, 0],
        [2, 1, 2, 0],
        [2, 1, 1, 1],
        [1, 0, 1, 1]
    ])

    valid_moves = all_possible_moves(state=state, player=player)

    print(valid_moves)

    actuals = assert_valid_move(valid_moves, [
        (0, 2, expected_1),
        (0, 3, expected_2),
        (1, 3, expected_3),
        (3, 0, expected_4)
    ])

    for (actual, x, y, b) in actuals:
        if not actual:
            print(x, y, b)
        assert actual

def assert_valid_move(valid_moves, expected_list):
    actual = set()
    for (x, y, board) in valid_moves:
        b = str(board.reshape(1, len(board)**2))
        actual.add((x, y, b))

    expected = set()
    for (x, y, board) in expected_list:
        b = str(board.reshape(1, len(board)**2))
        expected.add((x, y, b))

    asserts = []
    for (x, y, board) in expected:
        if (x,y,board) not in actual:
            asserts.append((False, x, y,board))
        else:
            asserts.append((True, x, y, board))
    
    return asserts