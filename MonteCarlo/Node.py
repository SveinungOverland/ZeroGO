"""
Node for a moteCarlo treesearch
    contains:
    action: 
    state,
    parent
    terminate = False
"""
from math import sqrt, log

class Node:
    def __init__(self, action, state, parent, terminate = False, history=[]):
        self.visits = 0
        self.wins = 0
        self.action = action
        self.state = state
        self.history = history
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
            self.wins += 1

    def PUCT(self, opponent : bool, total_visits : int, c: float, naural_network_policy : float) -> float:
        Q = self.wins/self.visits
        U = c * naural_network_policy * sqrt(total_visits)/self.visits
        return Q + U if opponent else Q - U