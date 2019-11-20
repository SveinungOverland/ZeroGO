# Import and initialize the pygame library
import pygame
pygame.font.init()
from Go.game import Game
from Go.go import calculate_score, VALID_MOVE
from agent import Agent
import sys
import numpy as np
from threading import Thread
import argparse
import random
import os

from tkinter import *
import tkinter
from tkinter import messagebox
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo

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

        self.pass_button = Button(x=self.x, y=self.height + self.line_gap - 20,
        width=100, height=40, color=(255, 255, 255), screen=screen, text="Pass")

        self.save_button = Button(x=self.x + self.pass_button.width + 5, y=self.height + self.line_gap - 20,
        width=100, height=40, color=(255, 255, 255), screen=screen, text="Save")

        self.screen = screen
        self.last_move = None

        self.last_move_black = None
        self.last_move_white = None

        self.render_shadow = True

        # Animation stuff
        self.frame_count = 0
        self.game_to_animate = np.array([])
        self.last_player = 1


    def show(self, show_buttons=True):
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
        
        if self.last_move_black:
            x = int(self.x + self.last_move_black[1] * self.line_gap)
            y = int(self.y + self.last_move_black[0] * self.line_gap)
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), int(self.radius / 1.2), 1)
        
        if self.last_move_white:
            x = int(self.x + self.last_move_white[1] * self.line_gap)
            y = int(self.y + self.last_move_white[0] * self.line_gap)
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), int(self.radius / 1.2), 1)
        
        if show_buttons:
            self.pass_button.show()
            self.save_button.show()

    def place_piece(self, row, column):
        status = self.go.make_move(row, column)
        if status != VALID_MOVE: return

        self.board = self.go.get_board()

        self.is_black = self.go.get_current_turn() == 1
        self.last_move = (row, column)

    def move_shadow(self, row, column):
        self.shadow_piece = (row, column)
    
    def update_animation(self):
        self.frame_count += 1

        if self.frame_count % (FPS * interval) == 0:
            self.next_board()

    
    def next_board(self):
        if self.game_to_animate.size > 0:
            new_board = self.game_to_animate[0]
            

            found_change = False
            for row_index, row in enumerate(new_board):
                for col_index, _ in enumerate(row):
                    if new_board[row_index, col_index] != self.board[row_index, col_index]:
                        if new_board[row_index, col_index] == 1:
                            change_last_move_p1((row_index, col_index))
                        else:
                            change_last_move_p2((row_index, col_index))
                        found_change = True
                        break
            
            if not found_change:
                if self.last_player == 1:
                    change_last_move_p2((-1, -1))
                else:
                    change_last_move_p1((-1, -1))

            self.last_player = 2 if self.last_player == 1 else 1
            new_black_score, new_white_score, _ = calculate_score(new_board)
            change_black_score(new_black_score)
            change_white_score(new_white_score)
            
            self.board = new_board
            self.game_to_animate = self.game_to_animate[1:]

# Set up the drawing window
global screen

parser = argparse.ArgumentParser(description="Go game")
parser.add_argument("-mode", "--mode", type=str, help="Define players, (e.g 1v1, 1va, ava)", default="1va")
parser.add_argument("-path", "--path", type=str, help="Path for weights?", default="test_models/BestModel_7x7")
parser.add_argument("-dimension", "--dimension", type=int, help="Board dimension", default=7)
parser.add_argument("-loadfile", "--loadfile", type=str, help="Load board to animate", default=None)
parser.add_argument("-interval", "--interval", type=int, help="Seconds between each animation frame", default=2)
args = parser.parse_args()


screen = pygame.display.set_mode([600, 600])
global FPS
global interval
FPS = 60
interval = args.interval


board_width = 500
board_height = 500
dimension = 7
line_gap = board_width / dimension
board_x = 50 + line_gap / 2
board_y = 50 + line_gap / 2
text_size = 20

mode = args.mode
loadfile = args.loadfile
    

animate = loadfile != None

agent_black = Agent(1, dimension=dimension, steps=75)
agent_white = Agent(2, dimension=dimension, steps=75)

if args.path:
    agent_black.load(args.path)
    agent_white.load(args.path)

board = BoardView(screen, board_x, board_y, board_width, board_height, dimension=args.dimension)


def is_equal(n1, n2):
    for row1, row2 in zip(n1, n2):
        for col1, col2 in zip(row1, row2):
            if col1 != col2:
                return False
    return True


if loadfile:
    loaded_game = Game.load(file_path="saved_games/", file_name=loadfile)
    if is_equal(loaded_game[0], board.board):
        loaded_game = loaded_game[1:]
        board.last_player = 2

    board.game_to_animate = loaded_game


# Ultimate global variables with individual set method spaghetti mess.

global can_click_on_board
can_click_on_board = False
player1_turn = True

global last_move_p1
global last_move_p2
last_move_p1 = None
last_move_p2 = None

global black_score
global white_score
black_score = 0
white_score = 0

global confidence_black
global confidence_white
conf_b, _ = agent_black.predict(state=board.go.get_game_state(), player=1)
conf_w, _ = agent_black.predict(state=board.go.get_game_state(), player=2)
confidence_black = conf_b[0][0]
confidence_white = conf_w[0][0]

global paused
paused = False


def change_confidence_black(val):
    global confidence_black
    confidence_black = val

def change_confidence_white(val):
    global confidence_white
    confidence_white = val

def change_black_score(val):
    global black_score
    black_score = val

def change_white_score(val):
    global white_score
    white_score = val

def change_last_move_p1(val):
    global last_move_p1
    last_move_p1 = val
    board.last_move_black = val

def change_last_move_p2(val):
    global last_move_p2
    last_move_p2 = val
    board.last_move_white = val

def change_can_click_on_board(value):
    global can_click_on_board
    can_click_on_board = value

def change_player_turn(value):
    global player1_turn
    player1_turn = value

def change_paused(value):
    global paused
    paused = value

def player_move():
    change_can_click_on_board(True)

def agent_move():
    if player1_turn:
        x, y = agent_black.pick_action(state=board.go.get_game_state())
        print(f"Move: {x}, {y}")
        change_last_move_p1((x, y))
    else:
        x, y = agent_white.pick_action(state=board.go.get_game_state())
        print(f"Move: {x}, {y}")
        change_last_move_p2((x, y))

    board.go.make_move(x, y)
    board.board = board.go.get_board()
    board.is_black = not board.is_black
    change_player_turn(not player1_turn)
    execute_move()
    _, x, y = board.go.moves[-1]
    board.last_move = (x, y)

def random_move():
    if player1_turn:
        x, y = random.choice(agent_black.env.get_action_space(state=board.go.get_game_state(), player=1))[0]
        board.place_piece(x, y)
        change_player_turn(not player1_turn)
        execute_move()
        change_last_move_p1((x, y))
    else:
        x, y = random.choice(agent_black.env.get_action_space(state=board.go.get_game_state(), player=2))[0]
        board.place_piece(x, y)
        change_player_turn(not player1_turn)
        execute_move()
        change_last_move_p2((x, y))

def execute_move():
    new_black_score, new_white_score, _ = calculate_score(board.go.get_board())
    change_black_score(new_black_score)
    change_white_score(new_white_score)

    value_b, _ = agent_black.predict(state=board.go.get_game_state(), player=1)
    value_w, _ = agent_black.predict(state=board.go.get_game_state(), player=2)
    value_b = value_b[0][0]
    value_w = value_w[0][0]

    change_confidence_black(value_b)
    change_confidence_white(value_w)

    if player1_turn:
        thread = Thread(target=turns["player_1"], args=())
    else:
        thread = Thread(target=turns["player_2"], args=())
    
    thread.start()


def render_text(text, x, y, font_size=30, font="Arial"):
    font = pygame.font.SysFont(font, font_size)
    surface = font.render(text, False, (0, 0, 0))
    screen.blit(surface, (x, y))


player1_mode, player2_mode = mode.split("v")
if player1_mode == "p" or player1_mode == "1":
    player1 = player_move
elif player1_mode == "a":
    player1 = agent_move
elif player1_mode == "r":
    player1 = random_move
else:
    raise Exception("Fuck you mate, y u do dis? (Player1 mode is invalid)")

if player2_mode == "p" or player2_mode == "1":
    player2 = player_move
elif player2_mode == "a":
    player2 = agent_move
elif player2_mode == "r":
    player2 = random_move
else:
    raise Exception("Fuck you mate, y u do dis? (Player2 mode is invalid)")

if player1_mode != "p" and player1_mode != "1" and player2_mode != "1" and player2_mode != "p":
    board.render_shadow = False

turns = {
    "player_1": player1,
    "player_2": player2
}

# Run until the user asks to quit
running = True
if not animate:
    execute_move()
else:
    board.render_shadow = False


while running:
    if not animate:
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
                if board.pass_button.collision(x, y):
                    board.is_black = not board.is_black
                    board.go.do_pass()
                    if player1_turn:
                        change_last_move_p1((-1, -1))
                    else:
                        change_last_move_p2((-1, -1))

                elif board.save_button.collision(x, y):
                    Tk().wm_withdraw() #to hide the main window
                    
                    save_name = tkinter.simpledialog.askstring("Save game", "Type filename of this game")
                    save_name = "".join([save_name, ".npy"]) if not save_name.endswith(".npy") else save_name

                    board.go.save(file_path="./saved_games", file_name=save_name)
                    messagebox.showinfo("Save successful!", "The game is saved!")
                else:
                    row, column = board.shadow_piece
                    row = int(row)
                    column = int(column)
                    if row >= 0 and row < dimension and column >= 0 and column < dimension:
                        board.place_piece(row, column)
                        
                        if player1_turn:
                            change_last_move_p1((row, column))
                        else:
                            change_last_move_p2((row, column))
                
                change_can_click_on_board(False)
                change_player_turn(not player1_turn)
                execute_move()

        screen.fill((0, 0, 0))
        board.show()
    else:
        # Need this or the program will not run when animating.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    change_paused(not paused)
                elif event.key == pygame.K_RIGHT:
                    board.next_board()

        #delta_time = clock.tick(FPS) / 1000    # Seconds passed since previous frame
        if not paused:
            board.update_animation()
        else:
            #print("We are paused!")
            render_text(text="Paused", x=100, y=560, font_size=30)
        
        screen.fill((0, 0, 0))
        board.show(show_buttons=False)
        


    render_text(text="Player 1 last move: {}".format(last_move_p1), x=80, y=10, font_size=text_size)
    render_text(text="Player 2 last move: {}".format(last_move_p2), x=300, y=10, font_size=text_size)
    render_text(text="Player 1 score: {}".format(black_score), x=310, y=560, font_size=text_size)
    render_text(text="Player 2 score: {}".format(white_score), x=460, y=560, font_size=text_size)

    if paused:
        render_text(text="Paused", x=100, y=560, font_size=30)

    # Flip the display
    pygame.display.flip()