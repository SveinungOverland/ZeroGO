from ..mcts import MCTS
from ..node import Node
import numpy as np

class Mock_environment():
    def __init__(self):
        self.__player = 1

    def simulate(self, state, action, state_limit=3) -> tuple:
        return (np.zeros(shape = (9,9)), False)

    def get_action_space(self, state, player=None):
        return ((1,1), np.zeros(shape = (9,9)))

    def calculate_winner(self, state) -> int:
        return 1

    def rollout(self, state, start_player):
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

    def predict_policy(self, state: np.array, player: int) -> float:
        return np.zeros(shape = (5,5,3))

    def loss(self, z: int, v: int, pi: np.array, p: np.array, c: int, theta: np.array) -> float:
        return (z - v) ** 2 - pi.transpose().dot(np.log10(p))[0] + self.c * np.linalg.norm(theta)

    def __state_to_nn_input(self, state: np.array, player: int, N: int) -> np.array:
        return np.zeros(shape= (5,5,3))


mock_environment = Mock_environment()
mock_NN = Mock_NN()

mcts_object = MCTS(environment= mock_environment , neural_network= mock_NN, player_id= 1,steps = 1)





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

# Må få avklaring for choose node og metoder brukt i denne metoden


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
    children = [Node("best_one_here!", "state", mcts_object.root_node), Node("action", "state", mcts_object.root_node,1,True), Node("action", "state", mcts_object.root_node), Node("action", "state", mcts_object.root_node)]
    children[0].visits = 10
    children[0].wins = 10
    assert mcts_object.pick_action == children[0].action


def train_tree_search():
    mcts_object.root_node = Node((1,1), np.zeros(25), None)
    children = [Node("best_one_here!", "state", mcts_object.root_node), Node("action", "state", mcts_object.root_node,1,True), Node("action", "state", mcts_object.root_node), Node("action", "state", mcts_object.root_node)]
    children[0].visits = 10
    children[0].wins = 10
    mcts_object.tree_search(mcts_object.root_node)
    #checking if child 0 get a visit after the mc rollout inside the treeseach
    assert children[0].visits == 21
    #checking if the child got children and became a parent
    assert children[0].children == 0
    print(children[0].children) 








