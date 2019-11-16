from agent import Agent
from Go.go import all_possible_moves, PASS_MOVE, BLACK

import time
import random

def play_against_random(agent: Agent, verbose: bool = False):

    dimension = agent.env.get_dimension()
    state = agent.env.new_state()
    agent.initialize(state)

    agent_turn = True
    has_passed = False
    start = time.time()
    for _ in range(200):

        # Generate a move
        move = None
        current_player = agent.player
        if agent_turn:
            move = agent.pick_action(state)
        else:
            # Pick a random move
            current_player = agent.env.get_next_player(agent.player)
            moves = agent.env.get_action_space(state, current_player)
            if len(moves) == 0:
                # The opponent can not do anything
                break

            rand_index = random.randint(0, len(moves) - 1)
            move = moves[rand_index][0]
        move_x, move_y = move

        # Check for double pass
        if has_passed and move == PASS_MOVE:
            break
        has_passed = move == PASS_MOVE

        # Execute move
        state, done = agent.env.simulate(state, move, player=current_player)
        if verbose:
            print(f"{current_player.mcts.player_id} did action: {action}")
            print(state[-1])


        if done:
            break

        # Change turn
        agent_turn = not agent_turn

    end = time.time()

    winner = agent.env.calculate_winner(state)

    print(f"Winner: {winner}. Time: {end - start}s")
    return winner
        


best_agent = Agent(BLACK).load('./BestModel_5x5')

agent_wins = 0
random_wins = 0

for _ in range(10):
    winner = play_against_random(best_agent, verbose=True)

    if winner == agent.player:
        agent_wins += 1
    else:
        random_wins += 1

print(f"Agent win ratio {agent_wins}/{agent_wins + random_wins}. A: {agent_wins}, R: {random_wins}")



