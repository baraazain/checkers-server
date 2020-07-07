from .grid import Cell


class Action:

    def __init__(self, src, dst, player):
        self.id = -1
        self.src: Cell = src
        self.dst: Cell = dst
        self.player = player
        self.capture = None
        self.promote = False
        self.no_progress_count = 0

    def is_capture(self):
        return self.capture is not None

    def __str__(self):
        ret = "(" + str(self.src.r + 1) + ',' + str(self.src.c + 1) + ")"
        ret += "------->>>"
        ret += "(" + str(self.dst.r + 1) + "," + str(self.dst.c + 1) + ")"
        return ret

    def __eq__(self, other):
        if isinstance(other, Action):
            if self.src == other.src and self.dst == other.dst:
                if self.player == other.player and self.capture == other.capture:
                    return True
        return False
