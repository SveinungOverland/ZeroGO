from Go.go import *

import copy
import numbers
import numpy as np

TEST = 0

class Game:
    def __init__(self, size):
        self.board = np.zeros((size, size), dtype=int)
        self.history = [] # np.ndarrays
        self.moves = [] # [(x, y, player)]

        self.__player_turn = BLACK # Decides which player has the turn
        self.game_over = False

    def make_move(self, x, y):
        # Add a deep copy of the board to history
        self.history.append(copy.deepcopy(self.board))
        self.__store_move(self.__player_turn, x, y)

        # Make move
        board, status = execute_move(self.board, (self.__player_turn, x ,y), self.history)

        # Validate move
        if status != VALID_MOVE:
            self.__revert()
            return status

        self.__switch_turn()
        self.board = board
        return status

    def do_pass(self):
        # Pass
        self.moves.append((self.__player_turn, -1, -1))

        # Check if both players has passed, if so, declare end of game
        if len(self.moves) >= 2 and self.moves[-2][1] == -1 and self.moves[-2][2] == -1:
            self.game_over = True

        self.__switch_turn()
    
    def __switch_turn(self):
        self.__player_turn = BLACK if self.__player_turn == WHITE else WHITE

    def __store_move(self, player, x, y):
        self.moves.append((player, x, y))

    def get_board(self, raw=True):
        return self.board

    def get_current_turn(self):
        return self.__player_turn

    def get_score(self):
        return calculate_score(self.board)


    def __revert(self):
        '''
            Makes the game go back to the previous state (the previous turn)
        '''
        self.history.pop()
        self.moves.pop()

    def __str__(self):
        return board_to_string(self.board)


# game = Game(7)

# print(game)



# print(game.make_move( 1, 0))
# print(game.make_move( 2, 0))
# print(game.make_move( 3, 0))
# print(game.make_move( 4, 0))

# print(game)

# print(game.make_move( 0, 0))
# print(game)
# print(game.make_move( 1, 1))
# print(game)
# print(game.make_move( 2, 1))
# print(game)
# print(game.make_move( 3, 1))
# print(game)
# print(game.make_move( 4, 1))
# print(game)
# print(game.make_move( 5, 0))
# print(game)

# print(game.make_move( 5, 5))
# print(game.make_move( 3, 5))
# print(game.make_move( 4, 4))
# print(game.make_move( 4, 6))
# print(game)

# import time

# black, white, score_board = game.get_score()

# print("Score:")
# print(black, white)
# print(score_board)

# print(game.make_move( 2, 5))
# print(game.make_move( 3, 4))
# print(game.make_move( 3, 6))
# print(game)
# print(game.make_move( 4, 5))
# print(game)
# print(game.make_move( 3, 5))
# print(game)

# print("Score:")
# print(black, white)
# print(board_to_string(score_board))