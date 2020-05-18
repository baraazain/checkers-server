from math import floor, log10
import json


class Cell:

    def __init__(self, row, col, piece):
        self.r = row
        self.c = col
        self.piece = piece

    def setType(self, typ):
        self.piece.type = typ

    def getType(self):
        if self.piece is None:
            return None
        return self.piece.type

    def getColor(self):
        if self.piece is None:
            return None
        return self.piece.color

    def __str__(self):
        return "(" + str(self.r + 1) + "," + str(self.c + 1) + ")"

#    def __eq__(self, other):
#        return isinstance(other, Cell) and self.r == other.r and self.c == other.c and self.piece == other.piece


class Grid:

    def __init__(self, n=10, m=10):
        self.n = n
        self.m = m
        self.grid = [[Cell(i, j, None) for j in range(self.m)] for i in range(self.n)]

    def ok(self, r, c):
        return 0 <= r < self.n and 0 <= c < self.m

    def __str__(self):
        cnt_row = floor(log10(self.n)) + 1
        cnt_column = floor(log10(self.m)) + 1
        ret = str.center(" ", cnt_row + 2)
        for i in range(self.m):
            ret += str.center(str(i + 1), cnt_column + 1)
        ret += "\n"
        for i in range(self.n):
            ret += str.center(str(i + 1) + "|", cnt_row + 2)
            for j in range(self.m):
                if self.grid[i][j].piece is None:
                    ret += str.center(".", cnt_column + 1)
                else:
                    color = self.grid[i][j].getColor()
                    ret += str.center(color[0], cnt_column + 1)
            ret += "\n"
        return ret

    def __getitem__(self, item):
        return self.grid[item]

    def valid(self, cell: Cell) -> bool:
        return self.ok(cell.r, cell.c)