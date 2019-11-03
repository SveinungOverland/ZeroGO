# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '..\\..\..\..\AppData\Local\Temp'))
	print(os.getcwd())
except:
	pass
# %%
from nn import NNClient as NN
from MonteCarlo.mcts import MCTS
from Go.game import Game
from Go.go import BLACK, WHITE
from Go.environment import Environment

from datetime import datetime
import time


# %%
import mlflow.tensorflow
import mflux_ai

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
nn = NN(c, board_size, channel_size, residual_layers=30, filters=100)
agent = MCTS(Environment(), nn, BLACK, board_size, channel_size//2)


# %%
steps = 1
time_end = datetime.strptime('03/11/19 12:00:00', '%d/%m/%y %H:%M:%S').timestamp()
metric_upload_rate = 100
print(time_end)

# %%
mflux_ai.init("YQKDmPhMS9UuYEZ9hgZ8Fw")


# %%
elapsed_train_step = 0
iteration = 0
print(time.time())
while time_end > time.time():
    elapsed_train_step += 1
    metrics = agent.train(training_steps=steps)
    print(f"Iteration {iteration} complete!")

    if elapsed_train_step >= metric_upload_rate:
        print("Metrics: ", metrics)
        mlflow.log_param("version", "v1")
        mlflow.log_param("iteration", iteration)
        mlflow.log_metric("loss", metrics[0])
        mlflow.log_metric("value_loss", metrics[1])
        mlflow.log_metric("policy_loss", metrics[2])
        mlflow.log_metric("value_accuracy", metrics[3])
        mlflow.log_metric("policy_accuracy", metrics[4])

        mlflow.tensorflow.log_model(nn.get_model(), "model")

        elapsed_train_step = 0

        nn.get_model().save(f"models/{iteration}/")

    iteration += 1


# %%


