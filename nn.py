import numpy as np
from Go.environment import Environment
from NN.dcnn_v1 import Model, Mode, DataFormats

class NNClient:
    def __init__(self, c: float, dimension: int = 5, N: int = 3):
        self.c = c
        self.dimension = dimension
        self.model = Model.create(data_format=DataFormats.ChannelsLast)
        self.N = N

    def predict_policy(self, state: np.array, player: int) -> float:
        nn_input = self.__state_to_nn_input(state, player, self.N)
        return self.model.predict(Mode.Policy, nn_input)

    def predict(self, state: np.array, player: int) -> tuple:
        nn_input = self.__state_to_nn_input(state, player, self.N)
        policy = self.model.predict(Mode.Policy, nn_input)
        value = self.model.predict(Mode.Value, nn_input)

        return value, policy
    
    def train(self, state: np.array, player: int, z: float, pi: np.array):
        v, p = self.predict(state, player)
        theta = self.model.get_trunk_weights()
        loss = self.loss(z, v, pi, p, self.c, theta)

        self.model.train(Mode.Policy, loss)
        self.model.train(Mode.Value, loss)
    
    def loss(self, z: int, v: int, pi: np.array, p: np.array, c: int, theta: np.array) -> float:
        """
            l = (z - v)^2 - π^(T)*log(p) + c*||θ^2||
        """
        return (z - v) ** 2 - pi.transpose().dot(np.log10(p))[0] + self.c * np.linalg.norm(theta)


    def __state_to_nn_input(self, states: np.array, player: int, N: int) -> np.array:
        # This be correct padding?
        padding = N - len(states) * 2 - 1    # Calc number of empty arrays needed for padding


        # I heard you like readable code, so I made it in one line ^^
        return np.array([[[[1 if state[row][column] == color else 0 for color in range(1, 3) for state in states] + [player - 1] for column in range(self.dimension)] for row in range(self.dimension)]])