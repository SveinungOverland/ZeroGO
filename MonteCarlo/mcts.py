from MonteCarlo.node import Node
from MonteCarlo.buffer import Buffer
import numpy as np
import random
from math import sqrt
"""
Selection — you start in the root — the state, and select a child — a move. 
    I used the upper confident bound (UCB1) to select a child.
    For every child I calculated the expression: w/n+ c*sqrt(ln(N)/n) where w is the
    number of wins, n is the number time the node was visited, N is the number of times 
    the parent node was visited, and c is a factor which balanced between exploration and
    exploitation. This is the most crucial thing about MCTS. The most promising child 
    nodes are selected with a small chance to explore.

Expansion — when you get to a node where there are child nodes that have not yet 
been visited, pick one randomly and expand the tree.

Simulation — play random simulation until the game is over.

Back propagation — back propagate to all the visited nodes, increase by 1
    the visit number and if you win, increase by 1 the winning number.
"""
"""
enviroment consist of simulate, flatten
NN consists of train
"""
class MCTS:
    # add the enviroment that the MCTS is going to train on
    # add the neural_network, This network is created ahead, instead of created here. s
    def __init__(self,  enviroment, neural_network, player_id: int, steps: int = 1600, c: float = 1.0, tau: float = 1.2):
        self.enviroment = enviroment
        self.neural_network = neural_network
        self.buffer = Buffer()
        self.root_node = self.Node(None, None, None)
        self.player_id = player_id
        self.c = c
        self.tau = tau
        self.steps = steps


    def pick_action(self, state):

        for _ in range(self.steps):
            self.tree_search(self.root_node)

        action_space = []
        value = 0

        # Getting the total visits of  all the child nodes.
        total_visits = sum([child.visits for child in self.root_node.children])

        for child in self.root_node:
            # can try to add all of them into a 9x9 matrix representing what we would get.
            val =  self.stochasticly(child.visits, total_visits)
            if val > value:
                value = val
                new_action = child.action

            action_space.append(val)
        
        self.buffer.remember_upper_conf((self.root_node.state, action_space))
        return new_action
        
    def rollout(self, node: Node):
        done = node.terminate
        state = node.state

        while not done:
            state, done = self.enviroment.simulate(state, self.neural_network.find_best_action(state))
        win = self.enviroment.find_winner(state) == self.player_id

        self.back_propagation(node, win)

        
    def back_propagation(self, node: Node, win: bool):
        # reach the root node
        if(node == None):
            return
        node.visit()
        node.winning(win)
        self.back_propagation(node.parent, win)

    #chooses a node based on PUCT
    def choose_node(self, node: Node):
        total_visits = sum(child.visits for child in node.children)
        neural_policy, naural_value = self.neural_network.find_policy(node.state) # takes in the states and gives all policy values.
        # Med denne naural_network så er den i samme rekkefølge som barna, dette kan bli veldig fort feil.

        if node.state[0] == self.player_id:
            return np.array(node.PUCT(False, total_visits, self.c, neural_policy[index]) for (index, node) in enumerate(node.children)).argmax()
        else:
            return np.array(node.PUCT(True, total_visits, self.c, neural_policy[index]) for (index, node) in enumerate(node.children)).argmin()

    # assume that the state says who is playing, if its friendly or evil opponent
    def tree_search(self, node: Node):
        if node.children:
            self.tree_search(self.choose_node(node))
        else:
            # hit leaf_node. Expand this node.
            if node.visits == 0: 
                # the node has no visits and need rollout
                self.rollout(node)
            else:
                # Node has been visited and expands for all under
                node.children = [Node(action= action, state= state, parent= node) for (action, state) in self.enviroment.get_action_space(node.state)] #expanding node with all the posible actions and states.
                self.rollout(choose_node(node))


    def train(self, training_steps: int):
        for i in range(training_steps):
            state = self.enviroment.new_game(i % 2)
            done = False
            while not done:
                action = pick_action(state)
                done, state = self.enviroment.simulate(state, action)
            winner = self.enviroment.calculate_winner(state)

 # In trainning we want to add intelegent randomness and therefore use stochastic functions         
    def stochasticly(self, target_node: int, node_sum: int) -> float:
        return target_node**(1/self.tau) / node_sum**(1/self.tau)