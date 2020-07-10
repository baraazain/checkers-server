from .grid import Cell


class Color:
    WHITE = "WHITE"
    BLACK = "BLACK"


class Type:
    KING = "KING"
    PAWN = "PAWN"


class Piece:
    def __init__(self, cell: Cell, _type, color, dead=False):
        self.color = color
        self.type = _type
        self.cell = cell
        self.dead = dead

    @classmethod
    def from_dict(cls, dictionary):
        piece_cell = Cell.from_dict(dictionary['cell'])
        piece_type = dictionary['type']
        piece_color = dictionary['color']
        piece_dead = dictionary['dead']
        return cls(piece_cell, piece_type, piece_color, piece_dead)

    def __str__(self):
        return "(" + str(self.cell.r) + "," + str(self.cell.c) + "," \
               + self.color + ' ' + self.type + ")"

    def __eq__(self, other):
        if isinstance(other, Piece):
            if self.color == other.color and self.type == other.type and self.dead == other.dead:
                if self.cell is other.cell:
                    return True
                elif self.cell.r == other.cell.r and self.cell.c == other.cell.c:
                    return True
        return False

    def __hash__(self):
        return hash((self.color, self.type, self.dead,
                     self.cell.r, self.cell.c))
