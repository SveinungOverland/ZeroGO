# Simple pygame program
from boardview import BoardView

# Import and initialize the pygame library
import pygame

pygame.init()

# Set up the drawing window
global screen
screen = pygame.display.set_mode([500, 500])

board = BoardView(100, 100, 500, 500, dimension=9)

# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    board.show()

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()