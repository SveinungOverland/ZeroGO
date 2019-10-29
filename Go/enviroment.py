from go import *
import numpy as np
import random

class Enviroment:
    def __init__(self):
        self.__player = BLACK

    def simulate(self, state, action, history=None) -> tuple:
        """
            State is a n-dimensional numpy array with 0, 1 and 2s.
            Action is a n-dimensional numpy array with 0s except for one single 1-value that determines the move to take
        """
        # Convert action into (player, x, y)
        x, y = action
        new_action = (self.__player, x, y)

        # Execute new move
        new_state, status = execute_move(state=state, action=new_action, history=history)
        if status != VALID_MOVE:
            raise Exception(f"Invalid move for player {self.__player}: ({x}, {y}). Error-code: {status}\nState:\n{new_state}")

        # Add move to a copy of the history
        new_history = history.copy()
        new_history.append(new_state)

        # Check if we are done!
        other_player = opponent(self.__player)
        is_done = len(self.get_action_space(new_state, player=other_player, history=new_history)) == 0
        
        # Swap turn
        self.__player = other_player

        return new_state, is_done

    def get_action_space(self, state, history=None, player=None):
        if player == None:
            player = self.__player
        #returns all actions from given state (legal)
        return all_possible_moves(state, player, history)

    def calculate_winner(self, state) -> int:
        """
            Returns the winner of the given state
        """
        black_score, white_score, score_board = calculate_score(state)
        return BLACK if black_score > white_score else WHITE if white_score > black_score else TIE

    def get_player(self):
        return self.__player

    def set_player(self, player):
        self.__player = player

    @staticmethod
    def new_state(size=5):
        return np.zeros(shape=(size, size), dtype=int)

    @staticmethod
    def board_to_action(board):
        max_index = state.argmax()
        size = len(state)
        return (max_index // size, max_index % size)

    @staticmethod
    def generate_random_play(state, start_player):
        env = Enviroment()
        
        done = False
        history = []
        board = state.copy()
        while not done:
            
            moves = env.get_action_space(board, history=history)
            if len(moves) == 0:
                done = True
                continue
            move = moves[random.randint(0, len(moves) - 1)]
            move_x, move_y = move[0]
            board, done = env.simulate(board, (move_x, move_y), history=history)
            history.append(state)

        return env.calculate_winner(board)




b = np.zeros((5, 5), dtype=int)
winner = Enviroment.generate_random_play(b, BLACK)
print(winner)




