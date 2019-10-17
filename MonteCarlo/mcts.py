from MonteCarlo.Node import Node

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

"""
class MCTS:
    def __init__(self, enviroment, neural_network, ):
        pass

    
    def pass_action(self, state):
        pass


    def back_propagation(self, state, win):
        pass


    
