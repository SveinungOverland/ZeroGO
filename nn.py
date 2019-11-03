import numpy as np
from Go.environment import Environment
from NN.dcnn_v2 import Model, Mode, DataFormats

class NNClient:
    def __init__(self, c: float, dimension: int = 5, channel_size: int = 3, residual_layers: int = 10, filters=100):
        self.c = c
        self.dimension = dimension
        self.model = Model.create(data_format=DataFormats.ChannelsLast, shape=(5, 5, channel_size), kernel_size=(1, 1), nr_residual_layers=residual_layers, filters=filters)
        self.channel_size = channel_size

    def predict_policy(self, state: np.array, player: int) -> float:
        nn_input = self.__state_to_nn_input(state, player, self.channel_size)
        value, policy = self.model.predict(Mode.Model, nn_input)
        
        return policy

    def predict(self, state: np.array, player: int) -> tuple:
        nn_input = self.__state_to_nn_input(state, player, self.channel_size)
        value, policy = self.model.predict(Mode.Model, nn_input)
        
        return value, policy
    
    def train(self, state: np.array, player: int, z: float, pi: np.array):
        nn_input = self.__state_to_nn_input(state, player, self.channel_size)
        """ v, p = self.predict(state, player)
        theta = self.model.get_trunk_weights()
        loss = self.loss(z, v, pi, p[0], self.c, theta)[0][0]
        print("Loss: ", loss) """
        z = np.array([float(z)])
        pi = np.array([pi])

        return self.model.train(nn_input, z, pi, learning_rate=0.001)
    
    def loss(self, z: float, v: int, pi: np.array, p: np.array, c: int, theta: np.array) -> float:
        """
            l = (z - v)^2 - π^(T)*log(p) + c*||θ^2||
        """
        return (z - v) ** 2 - pi.transpose().dot(np.log10(p)) # + self.c * np.linalg.norm(theta)

    def get_model(self):
        return self.model.model

    def __state_to_nn_input(self, states: np.array, player: int, channel_size: int) -> np.array:
        # This be correct padding?
        padding = channel_size - len(states) * 2 - 1    # Calc number of empty arrays needed for padding
        wanted_state_size = channel_size//2

        dimension_3 = []
        for row in range(self.dimension):
            dimension_2 = []
            for column in range(self.dimension):
                cell = [1 if state[row][column] == 1 else 0 for state in states[-wanted_state_size:]] + [0 for _ in range(padding//2)] + [1 if state[row][column] == 2 else 0 for state in states[-wanted_state_size:]] + [0 for _ in range(padding//2)] + [player - 1]
                dimension_2.append(cell)
            dimension_3.append(dimension_2)

        nn_input = np.array([dimension_3], dtype=float)
        return nn_input
        # I heard you like readable code, so I made it in one line ^^
        #return np.array([[[[1 if state[row][column] == 1 else 0 for state in states] + [0 for _ in range(padding)] + [1 if state[row][column] == 2 else 0 for state in states] + [0 for _ in range(padding)] + [player - 1] for column in range(self.dimension)] for row in range(self.dimension)]])