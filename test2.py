# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

from nn import NNClient as NN
from MonteCarlo.mcts import MCTS
from Go.game import Game
from Go.go import BLACK, WHITE
from Go.environment import Environment

import traceback

# %% [markdown]
# ### Create the training environment

# %%
import os
os.environ["PATH"] += os.pathsep + 'C:/Users/Eier/Downloads/graphviz-2.38/release/bin/'


# %%
# Constants
board_size = 5
channel_size = 7
c = 1.5


# %%
agent_a = MCTS(Environment(), NN(c, board_size, channel_size), BLACK, board_size, channel_size//2)
agent_b = MCTS(Environment(), NN(c, board_size, channel_size), WHITE, board_size, channel_size//2)


# %%

agent_a.train(training_steps=1)


# %%


