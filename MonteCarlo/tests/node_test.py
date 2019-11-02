from ..node import Node
from math import sqrt
node = Node(None,None, None)

def test_create_node():
    assert isinstance(node, Node)

def test_node_winning():
    assert node.wins == 0
    node.winning(True)
    assert node.wins == 1

def test_node_visits():
    assert node.visits == 0
    node.visit()
    assert node.visits == 1



def test_parent():
    root = Node("action", "state", None)
    children = [Node("action", "state", root), Node("action", "state", root, 1,True), Node("action", "state", root), Node("action", "state", root)]
    root.children = children
    value = False

    for child in root.children:
        assert child.parent == root
        
        if child.terminate:
            value = True

    assert value


