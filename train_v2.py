from agent import Agent
from Go.go import BLACK, WHITE, PASS_MOVE
from nn import NNClient
import numpy as np
import time


def train(agent_a: Agent, agent_b: Agent, iterations: int = 1, max_game_iterations: int = 100, verbose: bool = False):
    
    metrics_a = None
    metrics_b = None

    for _ in range(iterations):
        # Initialize game state
        state = a.env.new_state()
        agent_a.initialize(state)
        agent_b.initialize(state)
        agent_a.mcts.buffer.clear()
        agent_b.mcts.buffer.clear()

        current_player = agent_a
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
            state, done = current_player.env.simulate(state, action, player=current_player.player)
            
            if verbose:
                print(f"{current_player.player} did action: {action}")
                print(state[-1])
            current_player = b if current_player == a else a

            if done:
                break
        
        end = time.time()

        # Calculate winner
        winner = current_player.env.calculate_winner(state)
        if verbose:
            print(f"Winner: {winner}. Time: {end - start}s")

        # Train
        buffer_a = agent_a.mcts.buffer
        buffer_b = agent_b.mcts.buffer
        metrics_a = a.train(winner == agent_a.player, buffer_b, verbose=verbose)
        metrics_b = b.train(winner == agent_b.player, buffer_a, verbose=verbose)


a = Agent(BLACK)
b = Agent(WHITE)

train(a, b, iterations=1, verbose=True)




