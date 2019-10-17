import pygame
from .go import screen


class BoardView:
    def __init__(self, x, y, width, height, dimension=9):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.dimension = dimension

        self.screen = screen

    def show(self):
        # Set background
        self.screen.fill((0, 0, 0))
        pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
