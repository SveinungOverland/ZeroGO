"""
Node for a moteCarlo treesearch
    contains:
    action: 
    state,
    parent
    terminate = False
"""
from math import sqrt, log, inf

class Node:
    def __init__(self, action, state, parent, player=1, terminate = False):
        self.visits = 0
        self.wins = 0
        self.action = action
        self.state = state
        self.terminate = terminate
        self.parent = parent
        self.player = player
        self.children = []

    #Policy uses upperboundpolicy π = w/n +(-) c*sqrt(ln(N)/n)
    #It changes from positive to minus, this depends on if it is the opponents turn 
    # Explore vs. Exploit
    def quality(self):
        return self.wins / (1 + self.visits)

    def visit(self):
        self.visits+=1

    def winning(self, won):
        if won:
            self.wins += 1

    def PUCT(self, opponent : bool, total_visits : int, c: float, naural_network_policy : float) -> float:
        if self.visits == 0:
            return inf

        Q = self.wins/self.visits
        U = c * naural_network_policy * sqrt(total_visits/self.visits)
        return Q + U if opponent else Q - U

    def UCB1(self,opponent: bool, total_visits : int, c: float) -> float:
        if self.visits == 0:
            return inf

        Q = self.wins/self.visits
        U = c * sqrt(total_visits/self.visits)
        return Q + U if opponent else Q - U