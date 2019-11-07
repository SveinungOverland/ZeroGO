from agent import Agent
from Go.go import BLACK, WHITE, PASS_MOVE
import numpy as np
import time

# Play_game plays a game between two agents and returns the player_id of the winner
def play_game(agent_a: Agent, agent_b: Agent, max_game_iterations: int, verbose: bool = False):
    # Initialize game state
    state = agent_a.env.new_state()
    agent_a.initialize(state)
    agent_b.initialize(state)

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
        current_player = agent_b if current_player == agent_a else agent_a

        # If done, stop the game
        if done:
            break
    
    end = time.time()

    # Calculate winner
    winner = current_player.env.calculate_winner(state)
    if verbose:
        print(f"Winner: {winner}. Time: {end - start}s")

    return winner

# PlayAndTrain trains players x amount of games between two different agains, trains after every game, and returns amount of wins and training metrics
# for each agent
def play_and_train(agent_a: Agent, agent_b: Agent, games_to_play: int = 1, max_game_iterations: int = 100, verbose: bool = False) -> tuple :
    
    metrics_a = None
    metrics_b = None

    agent_a_wins = 0
    agent_b_wins = 0

    for _ in range(games_to_play):
        agent_a.mcts.buffer.clear()
        agent_b.mcts.buffer.clear()

        # Play a game between the two agents
        winner = play_game(agent_a=agent_a, agent_b=agent_b, max_game_iterations=max_game_iterations, verbose=verbose)

        # Train based on the game
        buffer_a = agent_a.mcts.buffer
        buffer_b = agent_b.mcts.buffer
        metrics_a = agent_a.train(winner == agent_a.player, buffer_b, verbose=verbose)
        metrics_b = agent_b.train(winner == agent_b.player, buffer_a, verbose=verbose)
    
    return agent_a_wins, agent_b_wins, metrics_a, metrics_b

def train(agent_a: Agent, agent_b: Agent, stop_time: int, save_path: str):
    run_id = int(time.time())

    a = agent_a
    b = agent_b

    while stop_time > time.time():
        a_wins, b_wins, a_metrics, b_metrics = play_and_train(a, b, games_to_play=1, max_game_iterations=50, verbose=True)

        # Check who is the surviving agent
        if a_wins > b_wins:
            # Make new agent of b and save a
            b = Agent(b.player)


        else:
            # Make new agent of a and save b
            a = Agent(a.player)
    

a = Agent(BLACK)
b = Agent(WHITE)

time_end = datetime.strptime('06/12/19 14:00:00', '%d/%m/%y %H:%M:%S').timestamp()

train(a, b, iterations=1, stop_time=time_end, verbose=True)




