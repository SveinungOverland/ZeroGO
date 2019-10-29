import numpy as np
from Go.enviroment import Enviroment

class Adapter:
    def __init__(self, c: float, dimension: int = 5):
        self.c = c
        self.dimension = dimension
    
    def loss(self, policy, value, z: float, v: int, pi: np.array, p: np.array, c: int, theta: np.array) -> float:
        """
            l = (z - v)^2 - π^(T)*log(p) + c*||θ^2||
        """
        return (z - v) ** 2 - pi.transpose().dot(np.log10(p))[0] + self.c * np.linalg.norm(theta)


    def history_to_nn_input(self, state: np.array, player: int, N: int) -> np.array:
        padding = N - len(state)     # Calc number of empty arrays needed for padding

        for _ in range(padding):
            state = np.append(state, Enviroment.empty_board(size=self.dimension), axis=0)  # Add empty board as padding
        
        state = np.append(state, np.array([[player for _ in range(self.dimension)] for _ in range(self.dimension)]), axis=0)
        return state