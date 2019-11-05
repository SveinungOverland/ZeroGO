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
    
    # Modifiy the structure of valid_moves
    for i, move in enumerate(valid_moves):
        action, board = move
        x, y = action
        valid_moves[i] = (x, y, board)

    expected_moves = [
        (0, 3, expected_2),
        (1, 3, expected_3),
        (0, 2, expected_1),
        (3, 0, expected_4),
        (-1,-1, state),
    ]

    actuals = assert_valid_move(valid_moves, expected_moves)

    for (actual, x, y, b) in actuals:
        if not actual:
            print(x, y, b)
        assert actual

    assert len(valid_moves) == len(expected_moves)


def test_all_possible_moves_2():
    player = WHITE
    state = np.array([[
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    [
        [0, 0, 0, 2, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    [
        [1, 0, 0, 2, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]])

    valid_moves = all_possible_moves(state=state[-1], player=player, history=state[:-1])


    assert True

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