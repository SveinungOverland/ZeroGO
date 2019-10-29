import numpy as np
from Go.enviroment import Enviroment
from NN import Model, Mode

class NNClient:
    def __init__(self, c: float, dimension: int = 5, N: int):
        self.c = c
        self.dimension = dimension
        self.model = Model.create()
        self.N = N

    def predict_policy(self, state: np.array, player: int) -> float:
        nn_input = self.__state_to_nn_input(state, player, self.N)
        return self.model.predict(Mode.PolicyHead, nn_input)

    def predict(self, state: np.array, player: int) -> tuple:
        nn_input = self.__state_to_nn_input(state, player, self.N)
        policy = self.model.predict(Mode.PolicyHead, nn_input)
        value = self.model.predict(Mode.ValueHead, nn_input)

        return value, policy
    
    def train(self, state: np.array, player: int, z: float, pi: np.array):
        v, p = self.predict(state, player)
        theta = self.model.get_trunk_weights()
        loss = self.loss(z, v, pi, p, self.c, theta)

        self.model.train(Mode.PolicyHead, loss)
        self.model.train(Mode.ValueHead, loss)
    
    def loss(self, policy, value, z: float, v: int, pi: np.array, p: np.array, c: int, theta: np.array) -> float:
        """
            l = (z - v)^2 - π^(T)*log(p) + c*||θ^2||
        """
        return (z - v) ** 2 - pi.transpose().dot(np.log10(p))[0] + self.c * np.linalg.norm(theta)


    def __state_to_nn_input(self, state: np.array, player: int, N: int) -> np.array:
        padding = N - len(state)     # Calc number of empty arrays needed for padding

        for _ in range(padding):
            state = np.append(state, Enviroment.empty_board(size=self.dimension), axis=0)  # Add empty board as padding
        
        state = np.append(state, np.array([[player for _ in range(self.dimension)] for _ in range(self.dimension)]), axis=0)
        return state