import numpy as np
from point import Point

class Board:

    ERROR_INVALID_PLAYER = 21
    ERROR_INVALID_POINT = 22
    ERROR_OCCUPIED_POINT = 23

    def __init__(self, size):
        self.size = size
        self.board = np.ndarray(shape=(size, size), dtype=Point)
        for x in range(0, size):
            for y  in range(0, size):
                self.board[x, y] = Point(x, y)

    def make_move(self, player, x, y):
        # Check if player is either black or white
        if player != Point.BLACK and player != Point.WHITE:
            return Board.ERROR_INVALID_PLAYER, None
        
        if not self.__is_valid_slot(x, y):
            return Board.ERROR_INVALID_POINT, None

        if self.board[x,y].type != Point.EMPTY:
            return Board.ERROR_OCCUPIED_POINT, None

        # Make the move and calculate the changes
        self.board[x, y].type = player

        return self.board, self.board[x, y]


    def find_group_from_point(self, point):
        """
            Finds the group of a given points with DFS from the given point
        """

        # Initialize necassary variables
        group = []
        stack = []
        found = {}

        cur_node = (point.x, point.y)
        while cur_node is not None:
            x, y = cur_node

            # Check if the slot has been found previously or not
            if cur_node not in found:
                group.append(self.board[x, y])
                found[cur_node] = True
            
            # Find the next unfound neighbouring point 
            neighbours = self.board[x, y].get_neighbours(board=self.board, point_type=point.type)
            next_point = next(filter(lambda neighbour: (neighbour.x, neighbour.y) not in found, neighbours), None)

            # Set next point to check
            if next_point is None and len(stack) > 0:
                cur_node = stack.pop()
            elif next_point is not None:
                stack.append(cur_node)
                cur_node = (next_point.x, next_point.y)
            else:
                cur_node = None

        return np.array(group)

    def find_liberties(self, group):
        liberites = {}

        # For each point in the group, find it's liberties if not already found
        for point in group:
            if (point.x, point.y) in liberites:
                continue

            for liberty in point.find_liberties(board=self.board):
                liberites[(liberty.x, liberty.y)] = liberty
            
        return [liberty for ((x,y), liberty) in liberites.items()]

    def check_group_for_capture(self, group):
        '''
            Checks if the group is captured and if so removes the group
        '''
        liberties = self.find_liberties(group)
        opponent = group[0].opponent()

        # Check if some liberties is not occupied by a opponent
        for liberty in liberties:
            if liberty.type is not opponent:
                return False

        # The group is captured, remove the group from the board
        for point in group:
            point.type = Point.EMPTY

        return True
        
    def calculate_score(self):
        # TODO: Implement this method! :D 
        """
            Calculates the score for both BLACK and WHITE players, and returns count and a board with the belonging points
        """
        score_board = np.zeros((self.size, self.size), dtype=int)
        score_black = 0
        score_white = 0
        checked_points = {} # Dict to check if a given point has been checked or not
        
        for col_points in self.board:
            for point in col_points:
                if point.type is not Point.EMPTY or (point.x, point.y) in checked_points:
                    continue
       
                # Get the group
                group = self.find_group_from_point(point)
                liberties = self.find_liberties(group)

                # Check if the liberties contain only black or only whites
                has_found_white = False
                has_found_black = False
                for liberty in liberties:
                    if liberty.type == Point.BLACK:
                        has_found_black = True
                        if has_found_white:
                            break
                    elif liberty.type == Point.WHITE:
                        has_found_white = True
                        if has_found_black:
                            break
                
                # Calculate a score based on found pieces
                if has_found_black and not has_found_white:
                    score_black += len(group)
                    indices = np.array([[p.x, p.y] for p in group])
                    score_board[tuple(indices.transpose())] = Point.BLACK
                elif not has_found_black and has_found_white:
                    score_white += len(group)
                    indices = np.array([[p.x, p.y] for p in group])
                    score_board[tuple(indices.transpose())] = Point.WHITE
                
                # Mark group as found
                for group_point in group:
                    checked_points[(group_point.x, group_point.y)] = True
        
                

        return score_black, score_white, score_board

    def __is_valid_slot(self, x, y):
        # Check if x and y is in the borders of the board
        return x >= 0 or x < self.size or y >= 0 or y < self.size

    @staticmethod
    def board_to_string(board):
        output = ''
        is_point = isinstance(board[0, 0], Point)
        size = len(board)
        for col in range(0, size):
            for row in range(0, size):
                value = board[row, col].type if is_point else board[row, col]
                output += f'{int(value)}, '
            output += '\n'
        return output

    def __str__(self):
        return Board.board_to_string(board=self.board)
    