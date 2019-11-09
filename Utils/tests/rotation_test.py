import numpy as np
from ..rotation import rotate_training_data

def test_transpose_state_tests():
    # Initialize test data
    states = np.array([[[0,0],[2,0]],[[0,0],[2,0]]])
    policy = np.array([0.9,.1,.0,.8,.10101])

    new_state, new_policy = rotate_training_data(states, policy)

    assert np.array_equal(new_state, np.array([[[0,0],[0, 2]],[[0,0],[0, 2]]]))
    assert np.array_equal(new_policy, np.array([.1,.8,.9,0.,.10101]))