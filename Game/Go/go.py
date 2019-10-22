import numpy as np

EMPTY = 0
BLACK = 1
WHITE = 2

VALID_MOVE = 200
ERROR_INVALID_MOVE = 500
ERROR_OCCUPIED = 501
ERROR_SELF_CAPTURE = 502
ERROR_KO = 503

def execute_move(state, action, history=None):
    """
        Executes a given action ((player, x, y)) on a given state (numpy.ndarray)
        and returns the new state. The state here is a n*n go-board with 0, 1 and 2s.

        Action = (player, x, y) -> For example: (1, 3, 5)
        State = np.ndarray (n x n)
    """
    player, x, y = action
    opponent = BLACK if player == WHITE else WHITE
    size = len(state)

    # Check if the action is within the bounds
    if not is_within_bounds(state, x, y):
        return state, ERROR_INVALID_MOVE

    # Check if the position is occupied or not
    if state[x,y] != EMPTY:
        return state, ERROR_OCCUPIED

    # Make move
    board = state.copy()
    board[x,y] = player

    # Check for capturing
    opponent_points = get_neighbours(board, x, y, point_type=opponent)
    found = {} # A dict to keep track of which points have been checked
    captured_stones = 0
    for (point_x, point_y, _) in opponent_points:
        if (point_x, point_y) in found:
            continue

        # Find the group the given point belongs to
        group = find_group(board, point_x, point_y)

        # Mark the points in the found group as found
        for group_point in group:
            found[(group_point[0], group_point[1])] = True

        # Check if the group was captured, and if so, delete them
        was_captured = capture_group(board, group)
        if was_captured:
            captured_stones += len(group)
            

    # Check for self-capture
    if captured_stones == 0:
        group = find_group(board, x, y)
        was_captured = capture_group(board, group)
        if was_captured:
            # If was captured, reset the board. This is an illegal move
            return state, ERROR_SELF_CAPTURE

    # Check for KO
    if history is not None:
        if is_move_ko(board, x, y, history):
            return state, ERROR_KO

    return board, VALID_MOVE


def all_possible_moves(state, player):
    """
        Calculates all possible moves given a state (board) and a player (color). 
        It returns a list with all possible moves with the corresponding state (board) it produces. 

        State = np.ndarray (n x n)
        Player = int -> either 0 (empty), 1 (black) or 2 (white)        
    """
    oponent = BLACK if player == WHITE else WHITE
    board = state.copy()

    valid_moves = []
    
    for row_index, row in enumerate(board):
        for col_index, col in enumerate(row):
            if col != EMPTY: continue

            new_state, status = execute_move(board, (player, row_index, col_index))
            if status == VALID_MOVE:
                valid_moves.append((row_index, col_index, new_state))
    
    
    return valid_moves
    


def capture_group(board, group):
    '''
        Checks if the group is captured and if so removes the group from the given board
        The group is an array of tuples in form of (x, y)
    '''
    liberties = find_liberties(board, group)
    opponent = get_opponent(board, group[0][0], group[0][1])

    # Check if some liberties is not occupied by a opponent
    for (x,y) in liberties:
        if board[x,y] != opponent:
            return False # Is not captured

    # The group is captured, remove the group from the board
    for (x,y) in group:
        board[x,y] = EMPTY

    return True

def find_liberties(board, group):
    """
        Finds the liberties surrounding a given group.
        Group is an array of arrays with sublength 2 and this method 
        expects the type of each element in the group is the same.
        Returns an array of tuples in form of (x, y)
    """

    found_liberites = {}
    point_type = board[group[0][0], group[0][1]]

    # For each point in the group, find it's liberties if not already found
    for (point_x, point_y) in group:
        if (point_x, point_y) in found_liberites:
            continue
            
        # Get the neighbours that are not of the same type of point type
        neighbours = get_neighbours(board, point_x, point_y)
        liberties = np.array(list(filter(lambda neighbour: neighbour[2] != point_type, neighbours)))

        # Add the liberties to found_liberties
        for liberty in liberties:
            found_liberites[(liberty[0], liberty[1])] = liberty
     
    return np.array([(x,y) for ((x, y), liberty) in found_liberites.items()])

def find_group(board, start_x, start_y):
        """
            Finds the group of a given points with DFS from the given point
            Returns an array of (x, y) tuples
        """
        # Initialize necassary variables
        group = []
        stack = []
        found = {}
        point_type = board[start_x, start_y]

        cur_node = (start_x,start_y)
        while cur_node is not None:
            x, y = cur_node

            # Check if the slot has been found previously or not
            if cur_node not in found:
                group.append((x, y))
                found[cur_node] = True
            
            # Find the next unfound neighbouring point 
            neighbours = get_neighbours(board, x, y, point_type=point_type)
            next_point = next(filter(lambda neighbour: (neighbour[0], neighbour[1]) not in found, neighbours), None)

            # Set next point to check
            if next_point is None and len(stack) > 0:
                cur_node = stack.pop()
            elif next_point is not None:
                stack.append(cur_node)
                cur_node = (next_point[0], next_point[1])
            else:
                cur_node = None

        return np.array(group)

def get_neighbours(board, x, y, point_type=None):
    """
        Returns all the neighbours of a point in the form of (x, y, type)
    """
    size = len(board)

    # Get the neighbours of a given point
    neighbours = []
    if y - 1 >= 0:
        neighbours.append((x, y-1, board[x, y-1]))
    if y + 1 < size:
        neighbours.append((x, y + 1, board[x, y + 1]))
    if x - 1 >= 0:
        neighbours.append((x - 1, y, board[x-1, y]))
    if x + 1 < size:
        neighbours.append((x+1, y, board[x+1, y]))

    # If point_type is given, get all the points with the given type
    if point_type is not None:
        neighbours = list(filter(lambda point: point[2] == point_type, neighbours))

    return np.array(neighbours)

def get_opponent(board, x, y):
    return BLACK if board[x,y] == WHITE else WHITE

def is_within_bounds(board, x, y):
    # Check if x and y is in the borders of the board
    size = len(board)
    return x >= 0 or x < size or y >= 0 or y < size

def is_move_ko(board, x, y, history):
    # Can not be KO if there has not been more than 2 moves yet
    if len(history) <= 1:
        return False

    # The player has repeated it's move. Check if the board from two steps ago is equal to current board
    prev_board = history[-2]
    for i, row in enumerate(prev_board):
        for j, col in enumerate(row):
            if prev_board[i, j] != board[i, j]:
                return False

    return True

def calculate_score(board):
    """
        Calculates the score for both BLACK and WHITE players, and returns count and a board with the belonging points
    """
    size = len(board)
    score_board = np.zeros((size, size), dtype=int)
    score_black = 0
    score_white = 0
    checked_points = {} # Dict to check if a given point has been checked or not
    
    for x, rows in enumerate(board):
        for y, point_type in enumerate(rows):
            if point_type != EMPTY or (x, y) in checked_points:
                continue
    
            # Get the group
            group = find_group(board, x, y)
            liberties = find_liberties(board, group)

            # Check if the liberties contain only black or only whites
            has_found_white = False
            has_found_black = False
            for (lx, ly) in liberties:
                if board[lx,ly] == BLACK:
                    has_found_black = True
                    if has_found_white:
                        break
                elif board[lx,ly] == WHITE:
                    has_found_white = True
                    if has_found_black:
                        break
            
            # Calculate a score based on found pieces
            if has_found_black and not has_found_white:
                score_black += len(group)
                indices = np.array([[px, py] for (px, py) in group])
                score_board[tuple(indices.transpose())] = BLACK
            elif not has_found_black and has_found_white:
                score_white += len(group)
                indices = np.array([[px, py] for (px, py) in group])
                score_board[tuple(indices.transpose())] = WHITE
            
            # Mark group as found
            for (gx, gy) in group:
                checked_points[(gx, gy)] = True
    
    # Add the count of stones to the score
    temp = board.reshape(size*size)
    white_stones = len(list(filter(lambda x: x == WHITE, temp)))
    black_stones = len(list(filter(lambda x: x == BLACK, temp)))     

    return score_black + black_stones, score_white + white_stones, score_board

def board_to_string(board):
    output = ''
    size = len(board)
    for col in range(0, size):
        for row in range(0, size):
            output += f'{int(board[row, col])}, '
        output += '\n'
    return output