# Import and initialize the pygame library
import pygame
pygame.init()
from Go.game import Game

class BoardView:
    def __init__(self, screen, x, y, width, height, dimension=9):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.dimension = dimension
        #self.board = np.zeros([dimension, dimension])
        self.go = Game(dimension)
        self.board = self.go.get_board()
        self.shadow_piece = (int(dimension // 2), int(dimension // 2))
        self.line_gap = width / dimension

        self.radius = int(self.line_gap / 2.2)

        self.is_black = True

        self.screen = screen

    def show(self):
        # Set background
        self.screen.fill((237, 181, 101))

        for i in range(self.dimension):
            pygame.draw.line(self.screen, (0, 0, 0), (self.x, i * self.line_gap + self.y), (self.x + self.width - self.line_gap, i * self.line_gap + self.y), 2) # Horizontal
            pygame.draw.line(self.screen, (0, 0, 0), (i * self.line_gap + self.x, self.y), (i * self.line_gap + self.x, self.y + self.height - self.line_gap), 2) # Vertical


        piece_color = (0, 0, 0, 100) if self.is_black else (255, 255, 255, 100)

        #Render shadow piece
        row, col = self.shadow_piece
        x_pos = int(self.x + col * self.line_gap)
        y_pos = int(self.y + row * self.line_gap)
        pygame.draw.circle(self.screen, (piece_color), (x_pos, y_pos), int(self.radius - self.radius / 5))


        # Render all pieces.
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
        self.board = self.go.get_board()

        self.is_black = self.go.get_current_turn() == 1

    def move_shadow(self, row, column):
        self.shadow_piece = (row, column)

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

            if row >= 0 and row < dimension and column >= 0 and column < dimension:
                board.move_shadow(row=row, column=column)
        elif event.type == pygame.MOUSEBUTTONUP:
            row, column = board.shadow_piece
            row = int(row)
            column = int(column)
            if row >= 0 and row < dimension and column >= 0 and column < dimension:
                board.place_piece(row, column)


    screen.fill((0, 0, 0))
    board.show()

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()