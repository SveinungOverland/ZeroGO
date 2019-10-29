from ..mcts import MCTS
from ..node import Node
import numpy as np

class Mock_enviroment():
    def __init__(self):
        self.__player = 1

    def simulate(self, state, action, state_limit=3) -> tuple:
        return (np.zeros(shape = (9,9)), False)

    def get_action_space(self, state, player=None):
        return ("action", np.zeros(shape = (9,9)))

    def calculate_winner(self, state) -> int:
        return 1

    def random_play(self, state, history_size):
        return 1

    def get_player(self):
        return self.__player

    def set_player(self, player):
        self.__player = player

    def opponent(self, player):
        return 0

    def new_game(self):
        return np.zeros(shape = (9,9))


class Mock_NN():
    def find_policy(self, state):
        return (np.zeros(shape = (25)), 1)


mock_enviroment = Mock_enviroment()
mock_NN = Mock_NN()

mcts_object = MCTS(enviroment= mock_enviroment , neural_network= mock_NN, player_id= 1, board_size = 5,history_size = 3,steps = 1)

#testing the backpropagation of the mcts
def test_back_propagation():
    mcts_object.root_node = Node("action", np.zeros(shape = (1,9)), None)
    child_node = Node("action", np.zeros(shape = (1,9)), mcts_object.root_node)

    #adding children to the children to create a train of them
    for _ in range(10):
        child_node = Node((1,1), np.zeros(shape = (1,9)), child_node)

    mcts_object.back_propagation(child_node, True)

    #if the root node has one win and a visit that means the propagation went all the way back to the root node
    assert mcts_object.root_node.wins == 1
    assert mcts_object.root_node.visits == 1

    #oh no, we lost!
    mcts_object.back_propagation(child_node, False)

    assert mcts_object.root_node.wins == 1
    assert mcts_object.root_node.visits == 2

def test_choose_node():
    #create parent_node with children
    parent_node =  Node((1,1), np.zeros(shape = (1,9)), None)
    children = [Node((1,1), np.zeros(shape = (1,9)), parent_node), Node((1,1), np.zeros(shape = (1,9)), parent_node), Node((1,1), np.zeros(shape = (1,9)), parent_node)]
    children[0].visits = 10
    children[0].wins = 9
    parent_node.children = children
    assert children[0] == mcts_object.choose_node(parent_node)

def test_rollout():
    #create parent_node with children
    parent_node =  Node((1,1), np.zeros(shape = (1,9)), None)
    child_node = Node("action", np.zeros(shape = (1,9)), parent_node)

    #adding children to the children to create a train of them
    for _ in range(10):
        child_node = Node((1,1), np.zeros(shape = (1,9)), child_node)

    mcts_object.rollout(child_node)

    assert parent_node.wins == 1
    assert parent_node.visits == 1

def train_pick_action():
    mcts_object.root_node = Node((1,1), np.zeros(25), None)
    