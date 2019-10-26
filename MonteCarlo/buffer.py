
# data for each timestep is stored as (s_t,pi_t,z_t)
# saves all moves to the win or loose
class Buffer():
    def __init__(self):
        self.buffer = {}

    #Save the state and policy-values
    def remember_upper_conf(self,state, probabilites):
        self.buffer[state] = probabilites