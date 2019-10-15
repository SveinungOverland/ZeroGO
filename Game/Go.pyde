from Board import Board

# Making the board a global variable.
global board

# Method that runs before draw. Used for initializing variables and stuff.
def setup():
    size(600, 600)
    global board    
    board = Board(50, 50, 500, 500)

# Called every frame
def draw():
    background(255)
    board.show()

# Called every time the mouse is pressed.
def mousePressed():
    board.place_piece()

# Called every time you move your mouse
def mouseMoved():
   board.move_shadow(mouseX, mouseY)
