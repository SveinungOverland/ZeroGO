import numpy as np

class Point:

    # Define the board pieces
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = self.EMPTY
    
    def get_neighbours(self, board, point_type=None):
        x = self.x
        y = self.y
        size = len(board)

        # Get the neighbours of a given point
        neighbours = []
        if y - 1 >= 0:
            neighbours.append(board[x, y-1])
        if y + 1 < size:
            neighbours.append(board[x, y + 1])
        if x - 1 >= 0:
            neighbours.append(board[x-1, y])
        if x + 1 < size:
            neighbours.append(board[x+1, y])

        if point_type is not None:
            neighbours = list(filter(lambda point: point.type is point_type, neighbours))

        return np.array(neighbours)

    def find_liberties(self, board):
        neighbours = self.get_neighbours(board=board)
        return np.array(list(filter(lambda neighbour: neighbour.type is not self.type, neighbours)))

    def opponent(self):
        return Point.BLACK if self.type == Point.WHITE else Point.WHITE

    def point(self):
        return (self.x, self.y)

    def __str__(self):
        return f'({self.x}, {self.y})'