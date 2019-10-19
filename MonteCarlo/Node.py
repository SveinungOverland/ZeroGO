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
from math import sqrt, log
GAMMA = 0.3


class Node:
    def __init__(self, action, state, parent, terminate = False):
        self.visits = 0
        self.wins = 0
        self.action = action
        self.state = state
        self.terminate = terminate
        self.parent = parent
        self.children = []

    #Policy uses upperboundpolicy π = w/n +(-) c*sqrt(ln(N)/n)
    #It changes from positive to minus, this depends on if it is the opponents turn 
    # Explore vs. Exploit

    def visit(self):
        self.visits+=1

    def winning(self, won):
        if won:
            self.winning += 1

    def UCB1(self, opponent):
        return self.win/(1+self.visits) - GAMMA * sqrt(log(self.parent.visits)/(1+self.visits)) if opponent else self.win/(1+self.visits) + GAMMA * sqrt(log(self.parent.visits)/(1+self.visits))

