from agent import Agent
from Go.go import BLACK, WHITE, PASS_MOVE
import numpy as np
import time
import os
import random

import mlflow.keras
import mflux_ai

TRAINING_DATA_DIR = 'training_data'
TRAINING_DATA_FILE_NAME = 'training_data'
MODEL_DIR = 'model'

# Play_game plays a game between two agents and returns the player_id of the winner
def play_game(agent_a: Agent, agent_b: Agent, max_game_iterations: int, verbose: bool = False):

    player_1 = agent_a
    player_2 = agent_b

    # If agent_a is playing against itself
    if player_2 is None:
        player_2 = agent_a

    # Initialize game state
    state = player_1.env.new_state()
    player_1.initialize(state)
    player_2.initialize(state)

    current_player = player_1
    player_has_passed = False
    start = time.time()
    for i in range(max_game_iterations):
        # Generate a move
        action = current_player.pick_action(state)

        # Check if both players has passed
        if player_has_passed and action == PASS_MOVE:
            break
        player_has_passed = action == PASS_MOVE

        # Simulate move
        state, done = current_player.env.simulate(state, action, player=current_player.mcts.player_id)
        
        if verbose:
            print(f"{current_player.mcts.player_id} did action: {action}")
            print(state[-1])
        current_player = player_2 if current_player == player_1 else player_1

        # If done, stop the game
        if done:
            break

        # If agent_a is playing against it self, rotate the MCTS's player-id
        if agent_b is None:
            current_player.mcts.player_id = player_1.env.get_next_player(current_player.mcts.player_id)
    
    end = time.time()

    if agent_b is None:
        player_1.mcts.player_id = player_1.player

    # Calculate winner
    winner = player_1.env.calculate_winner(state)
    if verbose:
        print(f"Winner: {winner}. Time: {end - start}s")

    return winner

def save_and_log(agent: Agent, metrics: np.array, save_path: str, iteration: int, log: bool = True, overwrite: bool = False):
    if log:
        mflux_ai.init("YQKDmPhMS9UuYEZ9hgZ8Fw")

        # Log metrics and save model
        mlflow.log_param("version", "v2")
        mlflow.log_param("iteration", iteration)
        mlflow.log_metric("loss", metrics[0])
        mlflow.log_metric("value_loss", metrics[1])
        mlflow.log_metric("policy_loss", metrics[2])
        mlflow.log_metric("value_accuracy", metrics[3])
        mlflow.log_metric("policy_accuracy", metrics[4])

        mlflow.keras.log_model(agent.get_model(), "model")

    agent.save(f"{save_path}/{MODEL_DIR}", overwrite=overwrite)


def train_and_save(agent: Agent, games_to_play: int, save_path: str, max_game_iterations: int = 100, model_save_rate: int = -1, verbose: bool = False):
    run_id = int(time.time())

    if verbose:
        print(f"Agent starting to train {games_to_play} games against itself")

    metrics = None
    for i in range(games_to_play):
        # Play game
        agent.mcts.buffer.clear()
        winner = play_game(agent, None, max_game_iterations=max_game_iterations, verbose=verbose)

        # Train on result
        metrics = agent.train(winner == agent.player, verbose=verbose)

        # Save the training data
        if verbose:
            print("Starting to save training data")
        
        training_data = agent.mcts.buffer.data.copy()
        z = 1 if winner == agent.player else -1
        for j, data in enumerate(training_data):
            # Adding the winner to the training data
            training_data[j] = (data[0], data[1], z if i&1 == 0 else -z)
        training_data = np.array(training_data)
        np.save(f"{save_path}/{TRAINING_DATA_DIR}/{TRAINING_DATA_FILE_NAME}_{i}.npy", training_data)

        # Log and save model
        if (model_save_rate >= 0 and model_save_rate%i == 0) or model_save_rate == 0:
            save_and_log(agent, metrics, save_path, i, log=True, overwrite=True)

        if verbose:
            print(f"Finished training and saving game {i}/{games_to_play}")

    return metrics

def retrain(agent: Agent, training_batch: int, training_loops: int, save_path: str, verbose: bool = False):

    training_dir = f"{save_path}/{TRAINING_DATA_DIR}"

    # Get the amount of training files
    training_files_count = len([name for name in os.listdir(training_dir) if os.path.isfile(os.path.join(training_dir, name))])
    file_indicies = np.linspace(0, training_files_count - 1, training_files_count, dtype=int)
    start = time.time()
    metrics = None

    if verbose:
        print(f"Number of training files found: {training_files_count}")

    for loop_count in range(training_loops):
        if verbose:
            print(f"Starting training loop: {loop_count}/{training_loops}")

        # Get a random of order of the training files
        np.random.shuffle(file_indicies)

        # Load training data and train
        numb_of_trained_batches = 0
        for i in file_indicies:
            # Check if number of trained actions have exceeded for this training loop
            if numb_of_trained_batches >= training_batch:
                break
            
            # Extract training data
            training_data = np.load(f"{save_path}/{TRAINING_DATA_DIR}/{TRAINING_DATA_FILE_NAME}_{i}.npy")
            numb_of_trained_batches += len(training_data)
            
            # Train on training data
            for data in training_data:
                state = data[0]
                probabilities = data[1]
                z = int(data[2])
                metrics = agent.train_action(state, z, probabilities)

    if verbose:
        end = time.time()
        print(f"Finished all {training_loops} training loop in {end -start}s")    

    return metrics

def evaluate(agent_best: Agent, agent_latest: Agent, games_to_play: int, save_path: str, verbose: bool = False, verbose_play: bool = False) -> Agent:

    best_agent_wins = 0
    latest_agent_wins = 0

    for i in range(games_to_play):
        if verbose:
            print(f"Starting to play match {i}")

        # Play game between the agents
        winner = play_game(agent_best, agent_latest, max_game_iterations=60, verbose=verbose_play)

        # Evaluate the winner
        if winner == agent_best.player:
            best_agent_wins += 1
        else:
            latest_agent_wins += 1

        if verbose:
            print(f"The winner of game {i} is {winner}!")

    # Evaluate the games, if the latest player win over 55% percent of the games, new best player is declared
    latest_player_win_percentage = latest_agent_wins/games_to_play

    if verbose:
        print(f"Latest player won {latest_agent_wins}/{games_to_play} - {latest_player_win_percentage}%")

    if latest_player_win_percentage >= 0.55:
        return agent_latest
    return agent_best