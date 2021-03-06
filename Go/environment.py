from Go.go import (execute_move, opponent, all_possible_moves, calculate_score, BLACK, WHITE, TIE, VALID_MOVE, PASS_MOVE)
import numpy as np
import random

"""
All input "state"s are arrays of ndarrays
"""

class Environment:
    def __init__(self,  dimension: int = 5, max_state_size: int = 3, max_rollout_iterations: int = 100):
        self.dimension = dimension
        self.max_state_size = max_state_size
        self.max_rollout_iterations = max_rollout_iterations

    def simulate(self, state, action, player) -> tuple:
        """
            State is an array of n-dimensional numpy array with 0, 1 and 2s.
            Action is a tuple of (x, y)
            StateLimit is the limit of the state size of the output.
        """
        # Convert action into (player, x, y)
        x, y = action
        new_action = (player, x, y)

        # Extract last state and history
        current_state = state[-1]
        history = state[:len(state)-1]

        new_history = state.copy()
        # Execute move if the move is not a pass (PASS => Action = (-1, -1))
        if x != -1 and y != -1:
            # Execute new move
            new_state, status = execute_move(state=current_state, action=new_action, history=history)
            if status != VALID_MOVE:
                raise Exception(f"Invalid move for player {player}: ({x}, {y}). Error-code: {status}\nState:\n{new_state}")

            # Add move to a copy of the history
            new_history = np.append(new_history, new_state.reshape(1, self.dimension, self.dimension), axis=0)
        else:
            new_history = np.append(new_history, current_state.reshape(1, self.dimension, self.dimension), axis=0)
            

        # Check if we are done!
        other_player = opponent(player)
        is_done = len(self.get_action_space(state=new_history, player=other_player)) == 1

        if len(new_history) > self.max_state_size:
            new_history = new_history[len(new_history) - self.max_state_size:]

        return new_history, is_done

    def get_action_space(self, state, player):

        #returns all actions from given state (legal)
        action_space = all_possible_moves(state[-1], player, history=state[:len(state)-1])

        return action_space

    def calculate_winner(self, state) -> int:
        """
            Returns the winner of the given state
        """
        black_score, white_score, score_board = calculate_score(state[-1])
        return BLACK if black_score > white_score else WHITE if white_score > black_score else TIE

    def get_next_player(self, player):
        return opponent(player)

    def get_dimension(self):
        return self.dimension

    def new_state(self):
        return np.zeros(shape=(1, self.dimension, self.dimension), dtype=int)

    def empty_board(self):
        return np.zeros(shape=(self.dimension, self.dimension), dtype=int)

    def rollout(self, state: np.array, player: int, start_player: int):
        # Playing five random games with different aspect
        win1 = self.play_random(state=state, start_player=start_player)
        win2 = self.play_random(state=state, start_player=start_player)
        win3 = self.play_random(state=state, start_player=start_player, max_iterations=10)
        win4 = self.play_random(state=state, start_player=start_player, max_iterations=10)
        win5 = self.play_random(state=state, start_player=start_player, only_pass=True)

        wins = [win1, win2, win3, win4]
        if win5 == player:
            wins.append(win5)
        # Filter away ties (3)
        valid_games = [w for w in wins if w != 3]
        # Convert the wins to booleans, count the amount of wins, and if
        return sum([w == player for w in valid_games]) >= 2

    def play_random(self, state: np.array, start_player:int, max_iterations: int = None, only_pass: bool = False):
        if max_iterations is None:
            max_iterations = self.max_rollout_iterations

        done = False
        history = state.copy()
        
        iterations = 0
        current_player = start_player
        while not done and iterations < max_iterations:
            move = None
            if only_pass and iterations&1 == 0:
                move = PASS_MOVE
            else:
                # Get all valid movies
                moves = self.get_action_space(history, player=current_player)
                if len(moves) == 0:
                    done = True
                    continue
                
                # Select a random move
                rand_index = random.randint(0, len(moves) - 1)
                move = moves[rand_index][0]
            move_x, move_y = move

            # Execute move
            history, done = self.simulate(state=history, action=(move_x, move_y), player=current_player)
            current_player = self.get_next_player(current_player)
            iterations += 1
        return self.calculate_winner(history)
