from MonteCarlo.node import Node
import numpy as np
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
    def __init__(self, enviroment, neural_network, player_id):
        self.enviroment = enviroment
        self.neural_network = neural_network
        self.root_node = Node(None, None, None)
        self.player_id = player_id

    #self.enviroment.simulate(state, action)
    def rollout(self, node):
        done = node.terminate
        state = node.state

        while not done:
            state, done = self.enviroment.simulate(state, neural_network.find_best_action(state))
        win = self.enviroment.find_winner() == self.player_id
        self.back_propagation(node, win)
        
    def back_propagation(self, node, win):
        # reach the root node
        if(node == None):
            return
        node.visit()
        node.winning(win)
        self.back_propagation(node.parent, win)

    def choose_node(self, node):
        if node.state[0] == self.player_id:
            return np.array(node.UCB1(False) for node in node.children).argmax()
        else:
            return np.array(node.UCB1(True) for node in node.children).argmin()

    # assume that the state says who is playing, if its friendly or evil opponent
    def tree_search(self, node):
        if node.children:
            self.tree_seach(choose_node(node))
        else:
            # hit leaf_node. Expand this node.
            if node.visits >= 0: 
                rollout(node)
            else:
                node.children = [Node(action= action, state= state, parent= node) for (action, state) in self.enviroment.get_action_and_state_from_state(node.state)] #expanding node with all the posible actions and states.
                rollout(choose_node(node))

            
            


