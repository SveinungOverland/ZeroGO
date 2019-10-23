"""
Node for a moteCarlo treesearch
    contains:
    action: 
    state,
    parent
    terminate = False
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

