from Go.go import (execute_move, opponent, all_possible_moves, calculate_score, BLACK, WHITE, TIE, VALID_MOVE)
import numpy as np
import random

"""
All input "state"s are arrays of ndarrays
"""

class Environment:
    def __init__(self):
        self.__player = BLACK

    def simulate(self, state, action, state_limit=3) -> tuple:
        """
            State is an array of n-dimensional numpy array with 0, 1 and 2s.
            Action is a tuple of (x, y)
            StateLimit is the limit of the state size of the output.
        """
        # Convert action into (player, x, y)
        x, y = action
        new_action = (self.__player, x, y)

        # Extract last state and history
        current_state = state[-1]
        history = state[:len(state)-1]

        new_history = state.copy()
        # Execute move if the move is not a pass (PASS => Action = (-1, -1))
        if x != -1 and y != -1:
            # Execute new move
            new_state, status = execute_move(state=current_state, action=new_action, history=history)
            if status != VALID_MOVE:
                raise Exception(f"Invalid move for player {self.__player}: ({x}, {y}). Error-code: {status}\nState:\n{new_state}")

            # Add move to a copy of the history
            new_history = np.append(new_history, new_state.reshape(1, 5, 5), axis=0)

        # Check if we are done!
        other_player = opponent(self.__player)
        is_done = len(self.get_action_space(state=new_history, player=other_player)) == 1
        
        # Swap turn
        self.__player = other_player

        if len(new_history) > state_limit:
            new_history = new_history[len(new_history) - state_limit:]

        return new_history, is_done

    def get_action_space(self, state, player=None):
        if player == None:
            player = self.__player

        #returns all actions from given state (legal)
        action_space = all_possible_moves(state[-1], player, history=state[:len(state)-1])

        action_space.append(((-1, -1), state[-1]))
        return action_space

    def calculate_winner(self, state) -> int:
        """
            Returns the winner of the given state
        """
        black_score, white_score, score_board = calculate_score(state[-1])
        return BLACK if black_score > white_score else WHITE if white_score > black_score else TIE

    def get_player(self):
        return self.__player

    def set_player(self, player):
        self.__player = player

    def get_opponent(self, player):
        return opponent(player)

    @staticmethod
    def new_state(size=5):
        return np.zeros(shape=(1, size, size), dtype=int)

    @staticmethod
    def empty_board(size=5):
        return np.zeros(shape=(size, size), dtype=int)

    def random_play(self, state: np.array, state_limit: int = 3, max_iterations: int = 200):
        done = False
        history = state.copy()
        
        iterations = 0
        while not done and iterations < max_iterations:
            # Get all valid movies
            moves = self.get_action_space(history)
            if len(moves) == 0:
                done = True
                continue
            
            # Select a random move
            rand_index = random.randint(0, len(moves) - 1)
            move = moves[rand_index]
            move_x, move_y = move[0]

            # Execute move
            history, done = self.simulate(history, (move_x, move_y), state_limit=state_limit)

            iterations += 1
        return self.calculate_winner(history)





