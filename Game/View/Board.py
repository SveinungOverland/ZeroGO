from Piece import Piece

class Board:
    def __init__(self, x, y, w, h, dimension=9):     
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dimension = dimension - 1
        self.line_gap = w / self.dimension
        
        self.board = [[None for i in range(dimension)] for i in range(dimension)]
        self.piece_shadow = None
        
        self.black_color = True
        global radius
        radius = self.line_gap / 1.25
    
    # Renders the board with all the pieces.
    def show(self):
        # Shows the background of the board, which is basically a brown square.
        fill(237, 181, 101)
        rect(self.x, self.y, self.w, self.h)
        
        # Creates the lines both vertically and horizontally.
        strokeWeight(2)
        for i in range(self.dimension):
            line(self.x, self.y + i * self.line_gap, self.x + self.w, self.y + i * self.line_gap)
            line(self.x + self.line_gap * i, self.y, self.x + self.line_gap * i, self.y + self.h)
        
        # Renders the shadow piece, which is the current piece to place.
        if self.piece_shadow != None:
            fill(0 if self.black_color else 255, 100)
            row_index, column_index = self.piece_shadow
            ellipse(column_index * self.line_gap + self.x, row_index * self.line_gap + self.y, radius, radius)
        
        
        # # Render all the pieces on the board.
        # for row in self.board:
        #     for cell in row:
        #         if cell != None:
        #             cell.show()
        
        [cell.show() for row in self.board for cell in row if cell != None] # Mad list comprehension.
    
    # Method called every time the mouse is moved so that the shadow can update.
    def move_shadow(self, mouse_x, mouse_y):
        if mouse_x < self.x or mouse_x > self.x + self.w or mouse_y < self.y or mouse_y > self.y + self.h:
            return
        
        actual_x = mouse_x - self.x + self.line_gap / 2
        actual_y = mouse_y - self.y + self.line_gap / 2
        row_index = actual_y // self.line_gap
        column_index = actual_x // self.line_gap
        
        self.piece_shadow = (row_index, column_index)
    
    # Places the piece where the mouse is currently hovering
    def place_piece(self):
        row_index, column_index = self.piece_shadow          # Indexes of the current piece you want to place.
        
        # Check that the piece you want to put is not on an already existing piece
        if self.board[row_index][column_index]:
            return
        
        self.board[row_index][column_index] = Piece(column_index * self.line_gap + self.x, row_index * self.line_gap + self.y, 0 if self.black_color else 255) # Places the new piece.
        self.black_color = not self.black_color   # Changes the color to the opposite.
    
    
    # Prints out the board, duh! For debugging purposes.
    def print_board(self):
        print("------------------------------------------------")
        for row in self.board:
            row_str = ""
            for cell in row:
                if cell == None:
                    row_str = " ".join([row_str, "0"])
                    continue
                
                if cell.colour == 0:
                    row_str = " ".join([row_str, "1"])
                    continue
                else:
                    row_str = " ".join([row_str, "2"])
                    continue
            print(row_str)
        print("------------------------------------------------")
