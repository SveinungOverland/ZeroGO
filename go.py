# Import and initialize the pygame library
import pygame
pygame.font.init()
from Go.game import Game
from agent import Agent
import sys
import numpy as np
from threading import Thread
import argparse

class Button:
    def __init__(self, x, y, width, height, color, screen, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.screen = screen
        self.text = text
    
    def show(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("Arial", 30)
        surface = font.render(self.text, False, (0, 0, 0))
        self.screen.blit(surface, (self.x + self.width / 5, self.y))
    
    def collision(self, x, y):
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height

class BoardView:
    def __init__(self, screen, x, y, width, height, dimension=9):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.dimension = dimension
        self.go = Game(dimension)
        self.board = self.go.get_board()
        self.shadow_piece = (int(dimension // 2), int(dimension // 2))
        self.line_gap = width / dimension

        self.radius = int(self.line_gap / 2.2)

        self.is_black = True
        self.button = Button(x=self.x, y=self.height + self.line_gap / 2,
        width=100, height=40, color=(255, 255, 255), screen=screen, text="Pass")
        self.screen = screen
        self.last_move = None

        self.render_shadow = True

    def show(self):
        # Set background
        self.screen.fill((237, 181, 101))

        for i in range(self.dimension):
            pygame.draw.line(self.screen, (0, 0, 0), (self.x, i * self.line_gap + self.y), (self.x + self.width - self.line_gap, i * self.line_gap + self.y), 2) # Horizontal
            pygame.draw.line(self.screen, (0, 0, 0), (i * self.line_gap + self.x, self.y), (i * self.line_gap + self.x, self.y + self.height - self.line_gap), 2) # Vertical


        piece_color = (0, 0, 0, 100) if self.is_black else (255, 255, 255, 100)

        if self.render_shadow:
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
        
        # Render last move ring
        if self.last_move:
            x = int(self.x + self.last_move[1] * self.line_gap)
            y = int(self.y + self.last_move[0] * self.line_gap)
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), int(self.radius / 1.2), 1)
        
        self.button.show()

    def place_piece(self, row, column):
        #self.board[row, column] = value
        status = self.go.make_move(row, column)
        self.board = self.go.get_board()

        self.is_black = self.go.get_current_turn() == 1
        self.last_move = (row, column)

    def move_shadow(self, row, column):
        self.shadow_piece = (row, column)

# Set up the drawing window
global screen
screen = pygame.display.set_mode([600, 600])

button = Button(x=100, y=100, width=100, height=40, color=(128, 128, 128), screen=screen, text="Pass")

board_width = 500
board_height = 500
dimension = 5
line_gap = board_width / dimension
board_x = 50 + line_gap / 2
board_y = 50 + line_gap / 2

board = BoardView(screen, board_x, board_y, board_width, board_height, dimension=dimension)

global can_click_on_board
can_click_on_board = False
player1_turn = True


agent_black = Agent(1)
agent_white = Agent(2)

def change_can_click_on_board(value):
    global can_click_on_board
    can_click_on_board = value

def change_player_turn(value):
    global player1_turn
    player1_turn = value

def player_move():
    change_can_click_on_board(True)

def agent_move():
    print("Current game state: {}".format(board.go.get_game_state()))
    if player1_turn:
        x, y = agent_black.pick_action(state=board.go.get_game_state())
        print(f"Move: {x}, {y}")
    else:
        x, y = agent_white.pick_action(state=board.go.get_game_state())
        print(f"Move: {x}, {y}")

    board.go.make_move(x, y)
    board.board = board.go.get_board()
    board.is_black = not board.is_black
    change_player_turn(not player1_turn)
    execute_move()
    player, x, y = board.go.moves[-1]
    board.last_move = (x, y)

def execute_move():
    if player1_turn:
        thread = Thread(target=turns["player_1"], args=())
    else:
        thread = Thread(target=turns["player_2"], args=())
    
    thread.start()

parser = argparse.ArgumentParser(description="Go game")
parser.add_argument("-mode", "--mode", type=str, help="Define players, (e.g 1v1, 1va, ava)", default="1va")

args = parser.parse_args()
mode = args.mode

if mode == "1v1":
    turns = {
        "player_1": player_move,
        "player_2": player_move
    }
elif mode == "1va":
    turns = {
        "player_1": player_move,
        "player_2": agent_move
    }
elif mode == "av1":
    turns = {
        "player_1": agent_move,
        "player_2": player_move
    }
elif mode == "ava":
    turns = {
        "player_1": agent_move,
        "player_2": agent_move
    }

    board.render_shadow = False
else:
    raise Exception("Fuck you mate, y u do dis?")

# Run until the user asks to quit
running = True
execute_move()
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
            if not can_click_on_board:
                continue

            x, y = pygame.mouse.get_pos()
            if board.button.collision(x, y):
                board.is_black = not board.is_black
                board.go.do_pass()
            else:
                row, column = board.shadow_piece
                row = int(row)
                column = int(column)
                if row >= 0 and row < dimension and column >= 0 and column < dimension:
                    board.place_piece(row, column)
            
            change_can_click_on_board(False)
            change_player_turn(not player1_turn)
            execute_move()



    screen.fill((0, 0, 0))
    board.show()

    # Flip the display
    pygame.display.flip()