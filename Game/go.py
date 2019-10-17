# Simple pygame program
from boardview import BoardView

# Import and initialize the pygame library
import pygame

pygame.init()

# Set up the drawing window
global screen
screen = pygame.display.set_mode([600, 600])

board_x = 50
board_y = 50
board_width = 500
board_height = 500
dimension = 5
line_gap = board_width / dimension

board = BoardView(screen, board_x, board_y, board_width, board_height, dimension=dimension)

# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            actual_x = x - board_x + line_gap / 2
            actual_y = y - board_y + line_gap / 2


            row = actual_y // line_gap
            column = actual_x // line_gap
            board.move_shadow(row=row, column=column)
        elif event.type == pygame.MOUSEBUTTONUP:
            row, column = board.shadow_piece
            row = int(row)
            column = int(column)
            board.place_piece(row, column)


    screen.fill((0, 0, 0))
    board.show()

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()