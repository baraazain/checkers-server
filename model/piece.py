from .grid import Cell
from copy import deepcopy


class Color:
    WHITE = "WHITE"
    BLACK = "BLACK"


class Type:
    KING = "KING"
    PAWN = "PAWN"


class Piece:
    def __init__(self, cell: Cell, _type, color):
        self.color = color
        self.type = _type
        self.cell = cell
        self.dead = False

    def from_object_to_dict(self):
        return {'color':self.color,'type':self.type,'dead':self.dead,'cell':None}

    @classmethod
    def from_dict_to_object(cls, dictionary):
        dictionary = deepcopy(dictionary)
        dictionary['cell'] = None
        p=Piece()
        p.__dict__ = dictionary
        return p

    def __str__(self):
        return "(" + self.cell.r + "," + self.cell.c + "," + self.color + ")"

    def __eq__(self, other):
        if isinstance(other, Piece):
            if self.color == other.color and self.type == other.type and self.dead == other.dead:
                if self.cell is other.cell:
                    return True
                elif self.cell.r == other.cell.r and self.cell.c == other.cell.c:
                    return True
        return False
