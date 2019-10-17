import Board

class Piece:
    # x = x position, duh
    # y = y position, also duh.
    # colour = the color of the piece (black/white), mega duh!
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.colour = colour

        global radius
        radius = Board.radius
    
    # Shows the piece
    def show(self):
        global radius
        fill(self.colour)
        ellipse(self.x, self.y, radius, radius)
