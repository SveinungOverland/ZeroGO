from MonteCarlo.mcts import MCTS
from MonteCarlo.buffer import Buffer
from NN.dcnn_v2 import Model, Mode, DataFormats
from Go.environment import Environment
from Go.go import BLACK, WHITE, PASS_MOVE
from nn import NNClient
import numpy as np
import time

class Candidate():
    def __init__(self, player: int):
        self.nn_wrapper = NNClient(c=1.0, dimension=5, channel_size=7, residual_layers=10, filters=100)
        self.env = Environment(dimension=5, max_state_size=3)
        self.mcts = MCTS(environment=self.env, neural_network=self.nn_wrapper, player_id=player, steps=50)
        self.player = player

    def initialize(self, state):
        self.mcts.initialize_root(state)

    def pick_action(self, state):
        return self.mcts.pick_action(state)

    def train(self, won: bool, other_buffer: Buffer, verbose: bool = False):
        training_iteration_count = len(other_buffer.data) + len(self.mcts.buffer.data)
        current_iteration_count = 0
        metrics = None

        if verbose:
            print("Starting training!")

        # Train on own buffer
        z = 1 if won else -1
        for (state, probabilities) in self.mcts.buffer.data:
            self.nn_wrapper.train(state, self.player, z, np.array(probabilities))
            current_iteration_count += 1
            if verbose:
                print(f"Training iteration: {current_iteration_count}/{training_iteration_count}")
        
        # Train on external buffer
        z = 1 if not won else -1
        for (state, probabilities) in other_buffer.data:
            metrics = self.nn_wrapper.train(state, self.player, z, np.array(probabilities))
            current_iteration_count += 1
            if verbose:
                print(f"Training iteration: {current_iteration_count}/{training_iteration_count}")

        if verbose:
            print("Training complete")

        return metrics


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

def train(agent_a: Candidate, agent_b: Candidate, iterations: int = 1, max_game_iterations: int = 100, verbose: bool = False):
    
    metrics_a = None
    metrics_b = None

    for _ in range(iterations):
        # Initialize game state
        state = a.env.new_state()
        a.initialize(state)
        b.initialize(state)
        a.mcts.buffer.clear()
        b.mcts.buffer.clear()

        current_player = a
        player_has_passed = False
        start = time.time()
        for i in range(max_game_iterations):
            # Generate a move
            action = current_player.pick_action(state)

            # Check if both players has passed
            if player_has_passed and action == PASS_MOVE:
                break
            player_has_passed = action == PASS_MOVE

            # Simulate move
            state, done = current_player.env.simulate(state, action, player=current_player.player)
            
            if verbose:
                print(f"{current_player.player} did action: {action}")
                print(state[-1])
            current_player = b if current_player == a else a

            if done:
                break
        
        end = time.time()

        # Calculate winner
        winner = current_player.env.calculate_winner(state)
        if verbose:
            print(f"Winner: {winner}. Time: {end - start}s")

        # Train
        buffer_a = a.mcts.buffer
        buffer_b = b.mcts.buffer
        metrics_a = a.train(winner == a.player, buffer_b, verbose=verbose)
        metrics_b = b.train(winner == b.player, buffer_a, verbose=verbose)


a = Candidate(BLACK)
b = Candidate(WHITE)

train(a, b, iterations=1, verbose=True)




