import numpy as np
from math import sqrt

def rotate_training_data(states : np.array, policy: np.array, k: int = 1) -> tuple:
    temp = []
    for state in states:
        temp.append(np.rot90(state, k=k))
    
    length_of_side = int(sqrt(policy.size-1))

    rotated_policy = np.append(np.rot90(policy[:-1].reshape(length_of_side,length_of_side), k=k).reshape(policy.size - 1), policy[-1])
    new_state = np.array(temp)
    return (new_state, rotated_policy)