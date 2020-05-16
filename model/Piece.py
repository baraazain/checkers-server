from .Grid import Cell
import json

class Color:
    WHITE = "WHITE"
    BLACK = "BLACK"


class Type:
    KING = "KING"
    PAWN = "PAWN"


class Piece(json.JSONEncoder):
    def __init__(self, cell: Cell, typ, color):
        self.color = color
        self.type = typ
        self.cell = cell

#    def __eq__(self, o):
#        return isinstance(o, Piece) and self.cell == o.cell and self.color == o.color and self.type == o.type

    def __str__(self):
        return "(" + self.cell.r + "," + self.cell.c + "," + self.color + ")"

    def default(self, obj):
        if isinstance(obj, Piece):
            return [obj.color, obj.type, json.dumps(obj.cell)]
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
