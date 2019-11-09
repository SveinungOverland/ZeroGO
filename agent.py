from MonteCarlo.mcts import MCTS
from MonteCarlo.buffer import Buffer
from Go.environment import Environment
from nn import NNClient
from NN.dcnn_v2 import Mode
import numpy as np
from Utils.rotation import rotate_training_data

c = 1.0
dimension = 5
channel_size = 7
residual_layers = 30
filters = 100
steps = 50

class Agent():
    def __init__(self, player: int):
        self.nn_wrapper: NNClient = NNClient(c=c, dimension=dimension, channel_size=channel_size, residual_layers=residual_layers, filters=filters)
        self.env: Environment = Environment(dimension=dimension, max_state_size=channel_size//2)
        self.mcts: MCTS = MCTS(environment=self.env, neural_network=self.nn_wrapper, player_id=player, steps=steps)
        self.player: int = player

        # Compile model
        self.nn_wrapper.model.compile_predict(Mode.Model)

    def initialize(self, state):
        self.mcts.initialize_root(state)

    def pick_action(self, state):
        return self.mcts.pick_action(state)

    def train(self, won: bool, verbose: bool = False):
        training_iteration_count = len(self.mcts.buffer.data)
    
        current_iteration_count = 0
        metrics = None

        if verbose:
            print("Starting training!")

        # Train on own buffer
        z = 1 if won else -1
        for (state, probabilities) in self.mcts.buffer.data:
            state2, prob2 = rotate_training_data(state, probabilities, k=1)
            state3, prob3 = rotate_training_data(state, probabilities, k=2)
            state4, prob4 = rotate_training_data(state, probabilities, k=3)
            metrics = self.nn_wrapper.train(state, self.player, z, np.array(probabilities))
            metrics = self.nn_wrapper.train(state2, self.player, z, np.array(prob2))
            metrics = self.nn_wrapper.train(state3, self.player, z, np.array(prob3))
            metrics = self.nn_wrapper.train(state4, self.player, z, np.array(prob4))
            current_iteration_count += 1
            if verbose:
                print(f"Training iteration: {current_iteration_count}/{training_iteration_count}")
            
            # Because next move represents the move of the opponent, the z value needs to be rotated
            z = 1 if z == -1 else -1
        
        if verbose:
            print("Training complete")

        return metrics

    def train_action(self, state: np.array, z: int, probabilities: np.array, player: int):
        return self.nn_wrapper.train(state, player, z, np.array(probabilities))

    def save(self, path, overwrite: bool = False):
        self.nn_wrapper.model.save(path, overwrite=overwrite)

    def get_model(self):
        return self.nn_wrapper.get_model()

    @classmethod
    def copy(cls, agent: 'Agent') -> 'Agent':
        c = cls.__new__(cls)
        c.env = agent.env
        c.nn_wrapper = agent.nn_wrapper
        c.player = agent.player
        c.mcts = MCTS(environment=agent.env, neural_network=agent.nn_wrapper, player_id=agent.player, steps=steps)
        return c