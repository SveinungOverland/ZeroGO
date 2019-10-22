from Go.go import *

class Enviroment:
    def __init__(self):
        self.__history = []
        self.__actions = []
        self.__player = BLACK

    def simulate(self, state, action):
        """
            State is a n-dimensional numpy array with 0, 1 and 2s.
            Action is a n-dimensional numpy array with 0s except for one single 1-value that determines the move to take
        """
        # Convert action into (player, x, y)
        max_index = state.argmax()
        size = len(state)
        action = (self.__player, max_index // size, max_index % size)

        # Execute new move
        new_state, status = execute_move(state=state, action=action, history=self.history)
        if status != VALID_MOVE:
            raise Exception("Fuck you! Invalid move! :D")

        # Check if we are done!
        opponent = opponent(self.__player)
        is_done = len(self.get_action_space(new_state, player=opponent)) == 0
        
        # Swap turn
        self.__player = opponent

        return new_state, is_done

    def get_action_space(self, state, player=None):
        if player == None:
            player = self.__player
        #returns all actions from given state (legal)
        return all_possible_moves(state, player)

    def calculate_winner(self, state) -> int:
        """
            Returns the winner of the given state
        """
        black_score, white_score, score_board = calculate_score(state)
        return BLACK if black_score > white_score else WHITE if white_score > black_score else TIE


