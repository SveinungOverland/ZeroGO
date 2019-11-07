from MonteCarlo.mcts import MCTS
from MonteCarlo.buffer import Buffer
from Go.environment import Environment
from nn import NNClient
import numpy as np


class Agent():
    def __init__(self, player: int):
        self.nn_wrapper: NNClient = NNClient(c=1.0, dimension=5, channel_size=7, residual_layers=10, filters=100)
        self.env: Environment = Environment(dimension=5, max_state_size=3)
        self.mcts: MCTS = MCTS(environment=self.env, neural_network=self.nn_wrapper, player_id=player, steps=50)
        self.player: int = player

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