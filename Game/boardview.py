import pygame
import numpy as np
from Go.go import Go

class BoardView:
    def __init__(self, screen, x, y, width, height, dimension=9):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.dimension = dimension
        #self.board = np.zeros([dimension, dimension])
        self.go = Go(dimension)
        self.board = self.go.get_board()
        self.shadow_piece = (int(dimension // 2), int(dimension // 2))
        self.line_gap = width / dimension

        self.radius = 20

        self.is_black = True

        self.screen = screen

    def show(self):
        # Set background
        self.screen.fill((237, 181, 101))

        for i in range(self.dimension):
            pygame.draw.line(self.screen, (0, 0, 0), (self.x, i * self.line_gap + self.y), (self.x + self.width - self.line_gap, i * self.line_gap + self.y), 2) # Horizontal
            pygame.draw.line(self.screen, (0, 0, 0), (i * self.line_gap + self.x, self.y), (i * self.line_gap + self.x, self.y + self.height - self.line_gap), 2) # Vertical


        piece_color = (0, 0, 0) if self.is_black else (255, 255, 255)

        #Render shadow piece
        row, col = self.shadow_piece
        x_pos = int(self.x + col * self.line_gap)
        y_pos = int(self.y + row * self.line_gap)
        pygame.draw.circle(self.screen, (piece_color), (x_pos, y_pos), self.radius)

        for row_index, row in enumerate(self.board):
            for col_index, col in enumerate(row):
                if col == 1:
                    x_pos = int(self.x + col_index * self.line_gap)
                    y_pos = int(self.y + row_index * self.line_gap)
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x_pos, y_pos), self.radius)
                elif col == 2:
                    x_pos = int(self.x + col_index * self.line_gap)
                    y_pos = int(self.y + row_index * self.line_gap)
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                       (x_pos, y_pos), self.radius)

    def place_piece(self, row, column):
        #self.board[row, column] = value
        status = self.go.make_move(row, column)
        print("History Length:", len(self.go.history))
        print(status)
        self.board = self.go.get_board()

        self.is_black = self.go.get_current_turn() == 1

    def move_shadow(self, row, column):
        self.shadow_piece = (row, column)