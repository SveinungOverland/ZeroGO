from ..node import Node
from math import sqrt
node = Node(None,None, None)

def test_create_node():
    assert isinstance(node, Node)

def test_node_winning():
    assert node.wins == 0
    node.winning()
    assert node.wins == 1

def test_node_visits():
    assert node.visits == 0
    node.visit()
    assert node.visits == 1

def test_node_PUCT():
    node_puct = Node(None,None,None)
    node_puct.winning()
    node_puct.visit()
    node_puct.visit()
    value = node_puct.PUCT(False,10, 1, .5)
    Q = node_puct/node_puct.visits
    U = 1 * .5 * sqrt(10)/node_puct.visits
    value1 = node_puct.PUCT(False,10, 1, .5)

    assert value == Q + U
    assert value1 == Q - U


def test_parent():
    root = Node("action", "state", None)
    children = [Node("action", "state", root), Node("action", "state", root, True), Node("action", "state", root), Node("action", "state", root)]
    root.children = children
    value = False

    for child in root.children:
        assert child.parent == root
        
        if child.terminate:
            value = True

    assert value


