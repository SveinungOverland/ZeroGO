from board import Board
from point import Point

import copy
import numbers
import numpy as np

class Go:

    ERROR_KO = "KO"
    ERROR_SELF_CAPTURE = "SELF_CAPTURE"
    ERROR_NOT_PLAYER_TURN = "NOT_PLAYER_TURN"

    VALID_MOVE = 0

    TURNS = {

    }

    def __init__(self, size):
        self.board = Board(size)
        self.history = [] # Board.board
        self.moves = [] # [(x, y, player)]
        self.captured_blacks = 0
        self.captured_whites = 0

        self.__player_turn = Point.BLACK # Decides which player has the turn
        self.game_over = False

    def make_move(self, x, y):
        status = self.__make_move(self.__player_turn, x, y)
        if status == Go.VALID_MOVE:
            self.__player_turn = Point.BLACK if self.__player_turn == Point.WHITE else Point.WHITE
        return status

    def do_pass(self):
        # Pass
        self.moves.append((self.__player_turn, -1, -1))

        # Check if both players has passed, if so, declare end of game
        if len(self.moves) >= 2 and self.moves[-2][1] == -1 and self.moves[-2][2] == -1:
            self.game_over = True

        self.__player_turn = Point.BLACK if self.__player_turn == Point.WHITE else Point.WHITE

    def __make_move(self, player, x, y):
        # Make move
        board, point = self.board.make_move(player, x, y)
        if isinstance(board, numbers.Number):
            # Something went wrong, return error code (board)
            return board

        # Check for capturing
        opponent = point.opponent()
        opponent_points = point.get_neighbours(board=board, point_type=opponent)
        found = {} # A dict to keep track of which points have been checked
        captured_stones = 0
        for point in opponent_points:
            if (point.x, point.y) in found:
                continue

            # Find the group the given point belongs to
            group = self.board.find_group_from_point(point)

            # Mark the points in the found group as found
            for group_point in group:
                found[(group_point.x, group_point.y)] = True

            # Check if the group was captured, and if so, delete them
            was_captured = self.board.check_group_for_capture(group)
            if was_captured:
                captured_stones += len(group)
                

        # Check for self-capture
        if captured_stones == 0:
            group = self.board.find_group_from_point(point)
            was_captured = self.board.check_group_for_capture(group)
            if was_captured:
                # If was captured, reset the board. This is an illegal move
                self.__pop()
                return Go.ERROR_SELF_CAPTURE

        # Check for KO
        if self.__is_move_ko(player, x, y):
            self.__pop()
            return Go.ERROR_KO

        # Update captured stones statistics
        if opponent == Point.BLACK:
            self.captured_blacks += captured_stones
        else:
            self.captured_whites += captured_stones

        # Add a deep copy of the board to history
        self.history.append(copy.deepcopy(self.board.board))
        self.__store_move(player, x, y)

        return Go.VALID_MOVE
        
    def __is_move_ko(self, player, x, y):
        # Can not be KO if there has not been more than 2 moves yet
        if len(self.moves) <= 1:
            return False

        # Can not be KO if the player does not repeats it's move
        if self.moves[-2][1] != x and self.moves[-2][2] != y:
            return False
        
        # The player has repeated it's move. Check if the board from two steps ago is equal to current board
        prev_board = self.history[-2]
        for i, x in enumerate(prev_board):
            for j, point in enumerate(x):
                if point.type is not self.board.board[i, j].type:
                    return False

        return True
    
    def __store_move(self, player, x, y):
        self.moves.append((player, x, y))

    def __pop(self):
        '''
            Makes the game go back to the previous state (the previous turn)
        '''
        self.board.board = self.history.pop()
        self.moves = self.moves[:-1]

    def __str__(self):
        return str(self.board)


game = Go(7)

print(game)



print(game.make_move( 1, 0))
print(game.make_move( 2, 0))
print(game.make_move( 3, 0))
print(game.make_move( 4, 0))

print(game)

print(game.make_move( 0, 0))
print(game)
print(game.make_move( 1, 1))
print(game)
print(game.make_move( 2, 1))
print(game)
print(game.make_move( 3, 1))
print(game)
print(game.make_move( 4, 1))
print(game)
print(game.make_move( 5, 0))
print(game)

print(game.make_move( 5, 5))
print(game.make_move( 3, 5))
print(game.make_move( 4, 4))
print(game.make_move( 4, 6))
print(game)

import time

black, white, score_board = game.board.calculate_score()

print("Score:")
print(black, white)
print(Board.board_to_string(score_board))

print(game.make_move( 2, 5))
print(game.make_move( 3, 4))
print(game.make_move( 3, 6))
print(game)
print(game.make_move( 4, 5))
print(game)
print(game.make_move( 3, 5))
print(game)

print("Score:")
print(black, white)
print(Board.board_to_string(score_board))

print("Black stones captured:", game.captured_whites)
print("White stones captured:", game.captured_blacks)
