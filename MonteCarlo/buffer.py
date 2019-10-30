
# data for each timestep is stored as (s_t, pi_t, z_t)
# saves all moves to the win or lose
class Buffer():
    def __init__(self):
        self.data = []

        # Win = 1, tie = 0 and loss = -1.
        self.result = None

    # Save the state and policy-values
    def remember_upper_conf(self, state, probabilites):
        self.data.append((state, probabilites))

    def clear(self):
        self.data = []