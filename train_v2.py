from agent import Agent
from Go.go import BLACK, WHITE, PASS_MOVE
import numpy as np
import time
import os
import random
from Utils.rotation import rotate_training_data

from multiprocessing import Process, Queue

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

def save_and_log(agent: Agent, metrics: np.array, save_path: str, iteration: int, log: bool = True, overwrite: bool = False, custom_save_path: str = None):
    # Save model
    path = f"{save_path}/{MODEL_DIR}" if custom_save_path is None else custom_save_path

    agent.save(path, overwrite=overwrite) 

    if log:
        try:
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
        except Exception as e:
            print(f"MFlux Error: {e}")

def play_game_multi(model_path: str, player: int, q: Queue, max_game_iterations: int):
    a = Agent(player).load(model_path)
    
    winner = play_game(a, None, max_game_iterations=max_game_iterations, verbose=True)

    training_data = a.mcts.buffer.data
    z = 1 if winner == a.player else -1
    for i, data in enumerate(training_data):
        # Adding the winner to the training data
        training_data[i] = (data[0], data[1], z if i&1 == 0 else -z)
    training_data = np.array(training_data)

    q.put(training_data)

    return training_data


def self_play_multi(agent: Agent, iterations: int, num_of_processes: int, save_path: str, training_data_save_path: str, max_game_iterations: int = 100, save_model: bool = True, verbose: bool = False):
    if verbose:
        print(f"Agent starting to train on {iterations*num_of_processes} games against itself!")

    metrics = None
    model_path = f"{save_path}/temp"

    for j in range(iterations):
        
        q = Queue()
        processes = []

        # Save model to file so it can be shared with the other processes
        agent.save(model_path)

        # Create processes to run the game
        for _ in range(num_of_processes):
            p = Process(target=play_game_multi, args=(model_path, agent.player, q, max_game_iterations,))
            p.start()
            processes.append(p)

        # Wait for the processes to finish
        for p in processes:
            p.join()

        # Get all the training data
        training_data = []
        while not q.empty():
            training_data.append(q.get())
        training_data = np.array(training_data)[0]

        print("[SELF_PLAY] Training Data Shape: ", training_data.shape)

        # Save the training data
        np.save(f"{training_data_save_path}/{TRAINING_DATA_DIR}/{TRAINING_DATA_FILE_NAME}_{int(time.time())}.npy", training_data)

        # Train on the training data
        for i, data in enumerate(training_data):
            state, probabilities, z = data[0], data[1], data[2]
            current_player = agent.player if i&1 == 0 else agent.env.get_next_player(agent.player)
            state2, prob2 = rotate_training_data(state, probabilities, k=1)
            state3, prob3 = rotate_training_data(state, probabilities, k=2)
            state4, prob4 = rotate_training_data(state, probabilities, k=3)
            metrics = agent.train_action(state, z, probabilities, player=current_player)
            metrics = agent.train_action(state2, z, prob2, player=current_player)
            metrics = agent.train_action(state3, z, prob3, player=current_player)
            metrics = agent.train_action(state4, z, prob4, player=current_player)

        # Log and save model
        if save_model:
            save_and_log(agent, metrics, save_path, i, log=False, overwrite=True)
        
        if verbose:
            print(f"Finished training on and saving {(j+1)*num_of_processes}/{iterations*num_of_processes} games")

    return metrics

def self_play(agent: Agent, games_to_play: int, save_path: str, training_data_save_path: str, max_game_iterations: int = 100, model_save_rate: int = -1, verbose: bool = False):

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
        np.save(f"{training_data_save_path}/{TRAINING_DATA_DIR}/{TRAINING_DATA_FILE_NAME}_{int(time.time())}.npy", training_data)

        # Log and save model
        if (model_save_rate > 0 and (i == 0 or model_save_rate%i == 0)) or model_save_rate == 0:
            save_and_log(agent, metrics, save_path, i, log=False, overwrite=True)

        if verbose:
            print(f"Finished training and saving game {i+1}/{games_to_play}")

    return metrics

def retrain(agent: Agent, training_batch: int, training_loops: int, training_data_save_path: str, verbose: bool = False):

    training_dir = f"{training_data_save_path}/{TRAINING_DATA_DIR}"

    # Get the amount of training files
    training_files = [name for name in os.listdir(training_dir) if os.path.isfile(os.path.join(training_dir, name))]
    training_files_count = len(training_files)
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
            file_name = training_files[i]
            training_data = np.load(f"{training_data_save_path}/{TRAINING_DATA_DIR}/{file_name}", allow_pickle=True)
            numb_of_trained_batches += len(training_data)
            
            print("Shape Training Data: ", training_data.shape)
            # Train on training data
            for data in training_data:
                state, probabilities = data[0], data[1]
                z = int(data[2])
                player = agent.player if z == -1 else agent.env.get_next_player(agent.player)
                # Rotate training data
                state2, prob2 = rotate_training_data(state, probabilities, k=1)
                state3, prob3 = rotate_training_data(state, probabilities, k=2)
                state4, prob4 = rotate_training_data(state, probabilities, k=3)
                metrics = agent.train_action(state, z, probabilities, player=player)
                metrics = agent.train_action(state2, z, prob2, player=player)
                metrics = agent.train_action(state3, z, prob3, player=player)
                metrics = agent.train_action(state4, z, prob4, player=player)

    if verbose:
        end = time.time()
        print(f"Finished all {training_loops} training loop in {end -start}s")    

    return metrics

def evaluate(agent_best: Agent, agent_latest: Agent, games_to_play: int, save_path: str, max_game_iterations: int = 60, verbose: bool = False, verbose_play: bool = False) -> Agent:

    best_agent_wins = 0
    latest_agent_wins = 0

    for i in range(games_to_play):
        if verbose:
            print(f"Starting to play match {i}")

        # Play game between the agents
        winner = play_game(agent_best, agent_latest, max_game_iterations=max_game_iterations, verbose=verbose_play)

        # Evaluate the winner
        if winner == agent_best.player:
            best_agent_wins += 1
        else:
            latest_agent_wins += 1

        if verbose:
            print(f"The winner of game {i} is {winner}! {i+1}/{games_to_play} games completed!")

        # Check if it is necessary to continue
        if latest_agent_wins/games_to_play >= 0.55 or best_agent_wins/games_to_play >= 0.55:
            break

    # Evaluate the games, if the latest player win over 55% percent of the games, new best player is declared
    latest_player_win_percentage = latest_agent_wins/games_to_play

    if verbose:
        print(f"Latest player won {latest_agent_wins}/{games_to_play} - {latest_player_win_percentage*100}%")

    if latest_player_win_percentage >= 0.55:
        return agent_latest
    return agent_best