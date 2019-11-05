from MonteCarlo.mcts import MCTS
from NN.dcnn_v2 import Model, Mode, DataFormats
from Go.environment import Environment
from Go.go import BLACK, WHITE
from nn import NNClient
import numpy as np

class Candidate():
    def __init__(self, player: int):
        self.nn_wrapper = NNClient(c=1.0, dimension=5, channel_size=7, residual_layers=10, filters=100)
        self.env = Environment(dimension=5, max_state_size=3)
        self.mcts = MCTS(environment=self.env, neural_network=self.nn_wrapper, player_id=player, steps=100)
        self.player = player

    def initialize(state):
        self.mcts.initialize_root(state)

    def pick_action(state):
        return self.mcts.pick_action(state)

a = Candidate(BLACK)
b = Candidate(WHITE)




""" state = np.array([
    [
        [0, 2, 2, 2, 2],
        [2, 1, 1, 1, 1],
        [2, 1, 2, 2, 1], 
        [0, 1, 2, 2, 1],
        [0, 1, 1, 0, 1],
    ]
])
 """

state = a.env.new_state()
a.mcts.initialize_root(state)
b.mcts.initialize_root(state)

current_player = a
for i in range(30):
    action = current_player.mcts.pick_action(state)
    state, done = current_player.env.simulate(state, action, player=current_player.player)
    print(f"{current_player.player} did action: {action}")
    print(state[-1])
    current_player = b if current_player == a else a

print(f"Winner: {current_player.env.calculate_winner(state)}")
