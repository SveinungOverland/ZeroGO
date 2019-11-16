from .node import Node
from .buffer import Buffer
import numpy as np
import random
from math import sqrt
import pydot # for visualizing the tree

import time
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

class MCTS:
    # add the environment that the MCTS is going to train on
    # add the neural_network, This network is created ahead, instead of created here. s
    def __init__(self,  environment , neural_network,  player_id: int, steps: int = 10, c: float = 1.0, tau: float = 1.2, vanilla: bool = False):
        self.environment = environment
        self.neural_network = neural_network
        self.buffer = Buffer()
        self.root_node = Node(None, None, None)
        self.player_id = player_id
        self.c = c
        self.tau = tau
        self.steps = steps
        self.vanilla = vanilla

    def initialize_root(self, state):
        self.root_node = Node(None, state, None, self.player_id)

    #Extends the MCT with both the neural network and MCTS and finds the best possible choice.
    def pick_action(self, state):
        self.initialize_root(state)
        
        for _ in range(self.steps):
            self.tree_search(self.root_node)

        return self.__find_best_action()


    def rollout(self, node: Node):
        win = self.environment.rollout(state=node.state, start_player=node.player) == self.player_id
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
        total_visits = node.visits # sum(child.visits for child in node.children)
        neural_policy = self.neural_network.predict_policy(node.state, node.player)[0] # takes in the states and gives all policy values.

        # Filter illegal moves from neural_policy
        filtered_neural_policies = []

        size = self.environment.get_dimension()

        for child in node.children:
            x, y = child.action
            filtered_neural_policies.append(neural_policy[x*size + y])
            
        if node.player == self.player_id:
            return node.children[np.array(list(node.PUCT(True, total_visits, self.c, filtered_neural_policies[index]) for (index, node) in enumerate(node.children))).argmax()]
        else:
            return node.children[np.array(list(node.PUCT(False, total_visits, self.c, filtered_neural_policies[index]) for (index, node) in enumerate(node.children))).argmin()]

    def choose_node_vanilla(self, node:Node):
        total_visits = node.visits
        if node.player == self.player_id:
            return node.children[np.array(list(node.UCB1(True, total_visits, self.c) for (index, node) in enumerate(node.children))).argmax()]
        else:
            return node.children[np.array(list(node.UCB1(False, total_visits, self.c) for (index, node) in enumerate(node.children))).argmin()]


    # assume that the state says who is playing, if its friendly or evil opponent
    def tree_search(self, node: Node):
        if len(node.children) > 0:
            self.tree_search(self.choose_node(node) if not self.vanilla else choose_node_vanilla(node))
        else:
            # hit leaf_node. Expand this node.
            if node.visits == 0: 
                # the node has no visits and need rollout
                self.rollout(node)
            else:
                # Node has been visited and expands for all under
                player_opponent = self.environment.get_next_player(node.player)
                node.children = [Node(action=action, state=self.__append_state(node.state, state), parent=node, player=player_opponent) for (action, state) in self.environment.get_action_space(node.state, node.player)] #expanding node with all the posible actions and states.
                if len(node.children) == 0:
                    return
                self.rollout(self.choose_node(node) if  not self.vanilla else choose_node_vanilla(node))


    def train(self, training_steps: int):
        for _ in range(training_steps):
            self.buffer.clear()
            state = self.environment.new_state()
            self.initialize_root(state)
            done = False
            metrics = None

            iteration_count = 0

            current_player = self.player_id
            while not done:
                action = self.pick_action(state)

                # print("Action: " , action)
                try:
                    state, done = self.environment.simulate(state, action, player=current_player)
                    current_player = self.environment.get_next_player(current_player)
                except Exception as e:
                    print(e)
                    print("Error State: ", state)
                iteration_count += 1
            winner = self.environment.calculate_winner(state)

            # For training, we want the winner value (z) to be between -1 and 1
            z = 1 # We won
            if winner != self.player_id:
                z = -1 # The opponent won

            # For each action done in all the game, calculate loss and train NN
            current_player = 1
            training_steps_done = 0
            num_of_training_steps = len(self.buffer.data)
            for (state, probabilities) in self.buffer.data:
                # Get values from the NN
                current_player = 2 if current_player == 1 else 1
                metrics = self.neural_network.train(state, current_player, z, np.array(probabilities))
                training_steps_done += 1
                print("Training progress: ", training_steps_done, "/", num_of_training_steps)
            print("Training complete!")
            return metrics

 # In trainning we want to add intelegent randomness and therefore use stochastic functions         
    def __stochasticly(self, target_node: int, node_sum: int) -> float:
        return target_node**(1/self.tau) / node_sum**(1/self.tau)

    # Helper function for the pick action fuction. Adds all the probabilities to a list to train on and gives the best action to pick action.
    def __find_best_action(self) -> tuple:
        present_node = self.root_node
        probabilities = np.zeros(shape=(self.environment.get_dimension()*self.environment.get_dimension() + 1))
        value = 0
        new_action = None
        # Getting the total visits of all the child nodes.
        total_visits = present_node.visits # sum([child.visits for child in present_node.children])

        for child in present_node.children:

            x, y = child.action

            # can try to add all of them into a 9x9 matrix representing what we would get.
            visit_probability =  self.__stochasticly(child.visits, total_visits)
            
            # If the childs probability is higher than the ones before that means to choose that one.
            if visit_probability > value:
                value = visit_probability
                new_action = child.action
                self.root_node = child

            probabilities[x*self.environment.get_dimension() + y] = visit_probability # .append(visit_probability)

        # Do we not need to save who is playing when running training sessions?
        self.buffer.remember_upper_conf(present_node.state, probabilities)

        #If the action is None that means a bug is somewhere in the code above.
        if new_action == None:
            raise ValueError("the new action is None!")
        return new_action

    def __index_to_action(self, index):
        return (index // self.environment.get_dimension(), index % self.environment.get_dimension())
        
    def __append_state(self, state, board):
        return np.append(state, board.reshape(1, self.environment.get_dimension(), self.environment.get_dimension()), axis=0)

    #visulize the node tree 
    def visualize_tree(self):
        graph = pydot.Dot(graph_type='graph')
        self.build_graph(None, self.root_node, graph)
        graph.write_png('graph.png')


    def build_graph(self, graph_root, tree_root, graph):
        node = pydot.Node(id(tree_root), style='filled', fillcolor='#{:02x}6930'.format(int(tree_root.quality() * 255), int(tree_root.quality() * 255)), label=',Q={:.3f}'.format(tree_root.quality()))
        graph.add_node(node)
        for child in tree_root.children:
            self.build_graph(node, child, graph)
        if graph_root:
            graph.add_edge(pydot.Edge(graph_root, node, label=str(tree_root.action)))