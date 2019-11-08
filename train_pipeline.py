from agent import Agent
from train_v2 import train_and_save, retrain, evaluate, save_and_log, TRAINING_DATA_DIR, TRAINING_DATA_FILE_NAME, MODEL_DIR
from Go.go import BLACK, WHITE
from datetime import datetime 
import time
import os

# THIS TRAINING PIPELINE IS BASED ON CURRENT CHEAT SHEET: https://miro.medium.com/max/4000/1*0pn33bETjYOimWjlqDLLNw.png

TRAIN_STOP_TIME = '06/12/19 14:00:00'
VERSION = 1

training_end_time = datetime.strptime(TRAIN_STOP_TIME, '%d/%m/%y %H:%M:%S').timestamp()
current_training_iteration = 0
best_agent = Agent(BLACK)
while training_end_time > time.time():
    run_id = int(time.time())
    save_path = f"models/v{VERSION}/{run_id}"

    # Make necessary directories
    necessary_dirs = [f"{save_path}/{TRAINING_DATA_DIR}", f"{save_path}/{MODEL_DIR}"]
    for directory in necessary_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # SELF PLAY
    best_metrics = train_and_save(best_agent, games_to_play=1, save_path=save_path, max_game_iterations=10, model_save_rate=0, verbose=True)

    # Log and save model
    save_and_log(best_agent, None, save_path=save_path, iteration=current_training_iteration, log=False, overwrite=True)

    # RETRAIN NETWORK
    # Creating a new agent that trains on the previous X amount of positions Y times
    latest_agent = Agent(WHITE)
    latest_metrics = retrain(latest_agent, training_batch=50, training_loops=1, save_path=save_path, verbose=True)

    # EVALUATE NETWORK
    # Evaluating and choosing between the latest_agent and the best_agent

    # Evaluate and pick best agent
    new_best_agent = evaluate(best_agent, latest_agent, games_to_play=3, save_path=save_path, verbose=True, verbose_play=True)
    
    metrics = None
    if new_best_agent == best_agent:
        metrics = best_metrics
    else:
        metrics = latest_metrics
    best_agent = new_best_agent

    # Save and log the best agent
    save_and_log(best_agent, metrics=metrics, save_path=save_path, iteration=current_training_iteration, log=True, overwrite=True)

    current_training_iteration += 1

