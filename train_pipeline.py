from agent import Agent
from train_v2 import self_play, retrain, evaluate, save_and_log, TRAINING_DATA_DIR, TRAINING_DATA_FILE_NAME, MODEL_DIR
from Go.go import BLACK, WHITE
from datetime import datetime 
import time
import os

# THIS TRAINING PIPELINE IS BASED ON CURRENT CHEAT SHEET: https://miro.medium.com/max/4000/1*0pn33bETjYOimWjlqDLLNw.png

TRAIN_STOP_TIME = '06/12/19 14:00:00'
VERSION = 1

training_end_time = datetime.strptime(TRAIN_STOP_TIME, '%d/%m/%y %H:%M:%S').timestamp()
current_training_iteration = 0

base_path = f"models/v{VERSION}"
best_agent_path = f"{base_path}/best"

best_agent = Agent(BLACK).load(model_path=best_agent_path)

while training_end_time > time.time():
    run_id = int(time.time())
    save_path = f"{base_path}/{run_id}"
    training_data_path = f"{base_path}/{TRAINING_DATA_DIR}"

    # Make necessary directories
    necessary_dirs = [training_data_path, f"{save_path}/{MODEL_DIR}", best_agent_path]
    for directory in necessary_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    start_time = time.time()

    # SELF PLAY
    print("\n\n-------- SELF PLAY ----------")
    best_metrics = self_play(best_agent, games_to_play=1, save_path=save_path, training_data_save_path=base_path, model_save_rate=0, max_game_iterations=2, verbose=True)

    # Log and save model
    save_and_log(best_agent, None, save_path=save_path, iteration=current_training_iteration, log=False, overwrite=True)

    # RETRAIN NETWORK
    # Creating a new agent that trains on the previous X amount of positions Y times
    print("\n\n-------- RETRAIN NETWORK ----------")
    latest_agent = Agent(WHITE)
    latest_metrics = retrain(latest_agent, training_batch=50, training_loops=1, training_data_save_path=base_path, verbose=True)

    # EVALUATE NETWORK
    # Evaluating and choosing between the latest_agent and the best_agent

    # Evaluate and pick best agent
    print("\n\n-------- EVALUATE ----------")
    new_best_agent = evaluate(best_agent, latest_agent, games_to_play=1, save_path=save_path, max_game_iterations=60, verbose=True, verbose_play=True)
    
    metrics = None
    if new_best_agent == best_agent:
        metrics = best_metrics
    else:
        metrics = latest_metrics
    best_agent = new_best_agent

    # Save and log the best agent
    save_and_log(best_agent, metrics=metrics, save_path=save_path, iteration=current_training_iteration, log=True, overwrite=True, custom_save_path=best_agent_path)
    save_and_log(best_agent, metrics=metrics, save_path=save_path, iteration=current_training_iteration, log=False, overwrite=True)

    current_training_iteration += 1

    end_time = time.time()

    print(f"Iteration {current_training_iteration} completed! Time used: {end_time - start_time}")

