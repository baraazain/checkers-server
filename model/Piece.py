from .Grid import Cell


class Color:
    WHITE = "WHITE"
    BLACK = "BLACK"


class Type:
    KING = "KING"
    PAWN = "PAWN"


class Piece:
    def __init__(self, cell: Cell, typ, color):
        self.color = color
        self.type = typ
        self.cell = cell

#    def __eq__(self, o):
#        return isinstance(o, Piece) and self.cell == o.cell and self.color == o.color and self.type == o.type

    def __str__(self):
        return "(" + self.cell.r + "," + self.cell.c + "," + self.color + ")"
