import copy

from .actors import Player
from .game import Game
from .action import Action
from .grid import Grid
from .piece import *


class TurkishGame(Game):
    @classmethod
    def build(cls, white_pieces: list, black_pieces: list, turn: int):
        game = cls(-1, None, None, None)
        game.white_pieces = copy.deepcopy(white_pieces)
        game.black_pieces = copy.deepcopy(black_pieces)
        game.current_turn = turn
        pieces = game.white_pieces + game.black_pieces
        for piece in pieces:
            if not piece.dead:
                game.grid[piece.cell.r][piece.cell.c].piece = piece
                piece.cell = game.grid[piece.cell.r][piece.cell.c]
        return game

    # for testing purposes
    @classmethod
    def read(cls):
        game = cls(-1, None, None, None)
        with open('input.txt') as f:
            for i in range(8):
                line = f.readline()
                j = 0
                for c in line:
                    if c != ' ':
                        if c == 'B':
                            piece = Piece(game.grid[i][j], Type.PAWN, Color.BLACK)
                            game.grid[i][j].piece = piece
                            game.black_pieces.append(piece)
                        if c == 'W':
                            piece = Piece(game.grid[i][j], Type.PAWN, Color.WHITE)
                            game.grid[i][j].piece = piece
                            game.white_pieces.append(piece)
                        j += 1
        return game

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = Grid(8, 8)

        # initialize the grid and add pieces to their respective array

    def init(self):
        for i in range(1, 3):
            for j in range(0, 8):
                piece = Piece(self.grid[i][j], Type.PAWN, Color.BLACK)
                self.grid[i][j].piece = piece
                self.black_pieces.append(piece)
                print(str(i) + "," + str(j))

        for i in range(5, 7):
            for j in range(0, 8):
                piece = Piece(self.grid[i][j], Type.PAWN, Color.WHITE)
                self.grid[i][j].piece = piece
                self.white_pieces.append(piece)

    """
        Check if the move is correct king walk or not.
        @param move the move to check.
        @return true if correct king walk and false otherwise.
    """

    def correct_king_walk(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        if src.get_type() != Type.KING:
            return False
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if (src_r != dst_r and src_c != dst_c) or (src_r == dst_r and src_c == dst_c):
            return False
        if src_r == dst_r:
            dir_r = 0
            dir_c = (dst_c - src_c) // abs(src_c - dst_c)
        else:
            dir_r = (dst_r - src_r) // abs(src_r - dst_r)
            dir_c = 0
        cur_r = src_r + dir_r
        cur_c = src_c + dir_c
        while cur_r != dst_r or cur_c != dst_c:
            if self.grid[cur_r][cur_c].piece is not None:
                return False
            cur_r += dir_r
            cur_c += dir_c
        return True

    """
        Check if the move is correct king eat or not.
        @param move the move to check.
        @return true if correct king eat and false otherwise.
    """

    def correct_king_eat(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if (src_r != dst_r and src_c != dst_c) or (src_r == dst_r and src_c == dst_c):
            return False
        if src_r == dst_r:
            dir_r = 0
            dir_c = (dst_c - src_c) // abs(src_c - dst_c)
        else:
            dir_r = (dst_r - src_r) // abs(src_r - dst_r)
            dir_c = 0
        cur_r = src_r + dir_r
        cur_c = src_c + dir_c
        cnt = 0
        while cur_r != dst_r or cur_c != dst_c:
            if self.grid[cur_r][cur_c].get_color() == src.get_color():
                return False
            if self.grid[cur_r][cur_c].piece is not None:
                cnt += 1
            cur_r += dir_r
            cur_c += dir_c
        return cnt == 1

    """
        Check if the move is correct soldier walk or not.
        @param move the move to check.
        @return true if correct pawn walk and false otherwise.
    """

    def correct_walk(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        if not self.grid.ok(dst.r, dst.c):
            return False
        if dst.piece is not None:
            return False
        if src.piece is None:
            return False
        r = src.r
        c = src.c
        ac = [-1, 1]
        if src.get_type() == Type.KING:
            return self.correct_king_walk(action)
        else:
            ar = [0, 0]
            for i in range(0, 2, 1):
                nr = r + ar[i]
                nc = c + ac[i]
                if nr == dst.r and nc == dst.c:
                    return True
            ac = 0
            if src.get_color() == Color.WHITE:
                ar = -1
                nr = r + ar
                nc = c + ac
                if nr == dst.r and nc == dst.c:
                    return True
            elif src.get_color() == Color.BLACK:
                ar = 1
                nr = r + ar
                nc = c + ac
                if nr == dst.r and nc == dst.c:
                    return True

        return False

    """
        Check if the move is correct soldier eat or not.
        @param move the move to check.
        @return true if correct pawn eat and false otherwise.
    """

    def correct_eat(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        if src.get_type() == Type.KING:
            return self.correct_king_eat(action)
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if not(src_r - dst_r == 0 and abs(src_c - dst_c) == 2):
            if src.get_color() == Color.WHITE:
                if not(src_r - dst_r == 2 and src_c - dst_c == 0):
                    return False
            elif src.get_color() == Color.BLACK:
                if not(src_r - dst_r == -2 and src_c - dst_c == 0):
                    return False

        middle_r = (src_r + dst_r) // 2
        middle_c = (src_c + dst_c) // 2
        middle_cell = self.grid[middle_r][middle_c]
        if middle_cell.piece is None:
            return False
        if middle_cell.get_color() == src.get_color():
            return False
        return True

    """
        Check if piece can walk horizontal diagonal.
        @param piece the piece to check.
        @return true if can walk horizontal and false otherwise.
    """

    def can_walk_horizontal(self, piece: Piece):
        src = piece.cell
        cur_r = src.r
        cur_c = 0
        dst = self.grid[cur_r][cur_c]
        action = Action(src, dst, None)
        if self.correct_walk(action):
            return True
        while cur_c < 7:
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        return False

    """
        Check if piece can walk vertical diagonal.
        @param piece the piece to check.
        @return true if can walk vertical and false otherwise.
    """

    def can_walk_vertical(self, piece: Piece):
        src = piece.cell
        cur_r = 1
        cur_c = src.c
        dst = self.grid[cur_r][cur_c]
        action = Action(src, dst, None)
        if self.correct_walk(action):
            return True
        while cur_r < 7:# cuR > 0
            cur_r += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        return False

    """
        Check if piece can eat horizontal diagonal.
        @param piece the piece to check.
        @return true if can eat horizontal and false otherwise.
    """

    def can_capture_horizontal(self, piece: Piece):
        src = piece.cell
        cur_r = src.r
        cur_c = 0
        dst = self.grid[cur_r][cur_c]
        action = Action(src, dst, None)
        if self.correct_eat(action):
            return True
        while cur_c < 7:
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        return False

    """
        Check if piece can eat vertical diagonal.
        @param piece the piece to check.
        @return true if can eat vertical and false otherwise.
    """

    def can_capture_vertical(self, piece: Piece):
        src = piece.cell
        cur_r = 0
        cur_c = src.c
        dst = self.grid[cur_r][cur_c]
        action = Action(src, dst, None)
        if self.correct_eat(action):
            return True
        while cur_r < 7:
            cur_r += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        return False

    def can_walk(self, piece):
        return self.can_walk_horizontal(piece) or self.can_walk_vertical(piece)

    def can_capture(self, piece):
        return self.can_capture_horizontal(piece) or self.can_capture_vertical(piece)

    def can_move(self, piece):
        return self.can_walk(piece) or self.can_capture(piece)

    """
        calc all possible walks in the horizontal diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_horizontal_walks(self, piece: Piece, current_player: Player):
        src = piece.cell
        st_r = src.r
        st_c = 0
        # (st_r, st_c) represents the first cell in the vertical diagonal
        actions = []
        while st_c < 8:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_walk(action):
                actions.append(action)
            # next cell in the vertical diagonal is (i+1, j+1)
            st_c += 1
        return actions

    """
        calc all possible walks in the vertical diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_vertical_walks(self, piece: Piece, current_player: Player):
        src = piece.cell
        st_r = 0
        st_c = src.c
        # (st_r, st_c) represents the first cell in the vertical diagonal
        actions = []
        while st_r < 8:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_walk(action):

                actions.append(action)
            # next cell in the vertical diagonal is (i+1, j-1)
            st_r += 1
        return actions

    """
        calc all possible eats in the horizontal diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_horizontal_captures(self, piece: Piece, current_player: Player):
        src = piece.cell
        st_r = src.r
        st_c = 0
        actions = []
        while st_c < 8:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_eat(action):
                actions.append(action)
            st_c += 1
        return actions

    """
        calc all possible eats in the vertical diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_vertical_captures(self, piece: Piece, current_player: Player):
        src = piece.cell
        st_r = 0
        st_c = src.c
        actions = []
        while st_r < 8:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_eat(action):
                actions.append(action)
            st_r += 1
        return actions

    """     
        @param src
        @return all possible moves starting from given cell
    """

    def get_all_possible_actions(self):
        actions = self.get_all_possible_captures()
        if not actions:
            actions = self.get_all_possible_walks()
        return actions

    # @return all possible walks from the current state
    def get_all_possible_walks(self):
        actions = []
        if self.current_turn == 1:
            # iterate over all white pieces and get the moves from the pieces
            for piece in self.white_pieces:
                if not piece.dead:
                    actions.extend(self.get_all_possible_horizontal_walks(piece, self.player1))
                    actions.extend(self.get_all_possible_vertical_walks(piece, self.player1))
        else:
            # iterate over all black pieces and get the moves for this pieces
            for piece in self.black_pieces:
                if not piece.dead:
                    actions.extend(self.get_all_possible_horizontal_walks(piece, self.player2))
                    actions.extend(self.get_all_possible_vertical_walks(piece, self.player2))
        paths = []
        for action in actions:
            arr = [action]
            paths.append(arr)

        return paths

    def get_maximum_captures(self, piece, player, cur_value):
        if not self.can_capture(piece):
            if self.mx == cur_value:
                self.paths.append(copy.deepcopy(self.path))

            if self.mx < cur_value:
                self.mx = cur_value
                self.paths.clear()
                self.paths.append(copy.deepcopy(self.path))

            return cur_value, self.paths

        captures = self.get_all_possible_horizontal_captures(piece, player)
        captures = captures + self.get_all_possible_vertical_captures(piece, player)

        for capture in captures:
            self.path.append(capture)
            self.apply_action(capture)
            self.get_maximum_captures(piece, player, 1 + cur_value)
            self.undo()
            self.path.pop()

        return self.mx, self.paths

    # @return all possible eats from cur_rent states
    def get_all_possible_captures(self):
        actions_value_pairs = []
        if self.current_turn == 1:
            # iterate over all white pieces and get the moves from the pieces
            for piece in self.white_pieces:
                if not piece.dead:
                    if self.can_capture(piece):
                        self.mx = 0
                        self.paths.clear()
                        actions_value_pairs.append(copy.deepcopy(self.get_maximum_captures(piece, self.player1, 0)))

        else:
            # iterate over all black pieces and get the moves from this pieces
            for piece in self.black_pieces:
                if not piece.dead:
                    if self.can_capture(piece):
                        self.mx = 0
                        self.paths.clear()
                        actions_value_pairs.append(copy.deepcopy(self.get_maximum_captures(piece, self.player2, 0)))

        mx = 0
        for value, _ in actions_value_pairs:
            mx = max(mx, value)

        captures = []
        for value, path in actions_value_pairs:
            if value == mx:
                captures.extend(path)

        return captures
    """      
        implements king's move
        @param move the king's move
    """

    def move_like_king(self, action: Action):
        src_r = action.src.r
        src_c = action.src.c
        dst_r = action.dst.r
        dst_c = action.dst.c
        src: Cell = action.src
        dst: Cell = action.dst

        # we remove the src piece and add the dst piece
        # remove the src piece
        # self.removePiece(src.piece)
        """
        No need to remove then add piece as we have the reference to the piece
        changes will apply in the list -_-
        """

        # move the piece from src to dst and empty src
        src.piece.cell = dst
        dst.piece = src.piece
        src.piece = None

        # add the dst piece
        # self.addPiece(dst.piece)

        # the direction that src has to move to reach dst.
        if src_r == dst_r:
            dirR = 0
            dirC = (dst_c - src_c) // abs(src_c - dst_c)
        else:
            dirR = (dst_r - src_r) // abs(src_r - dst_r)
            dirC = 0
        curR = src_r
        curC = src_c
        while curR != dst_r or curC != dst_c:
            cur: Cell = self.grid[curR][curC]
            """ 
                if we get reach to non-empty piece, so we need to erase it from
                the board (eat case)
            """
            if cur.piece is not None:
                action.eat = cur.piece
                cur.piece.dead = True
                # self.removePiece(cur.piece)
                cur.piece = None
                break
            curR += dirR
            curC += dirC
        if action.capture is not None and self.can_capture(self.grid[dst.r][dst.c].piece):
            return
        self.current_turn = 3 - self.current_turn
        # self.actions.append(action)

    """     
        @param move the move needs to implement
        @return if the given move can be implemented or not
    """

    def is_legal_path(self, path: list):
        for action in path:
            if not self.is_legal_action(action):
                return False
        return True

    def is_legal_action(self, action: Action):
        r = action.src.r
        c = action.src.c
        # Wrong turn
        if self.current_turn == 1 and self.grid[r][c].get_color() != Color.WHITE:
            return False
        if self.current_turn == 2 and self.grid[r][c].get_color() != Color.BLACK:
            return False
        action = self._validate_action(action)
        if self.correct_eat(action) or self.correct_walk(action):
            return True
        return False

    def _validate_action(self, action):
        src: Cell = action.src
        dst: Cell = action.dst
        src: Cell = self.grid[src.r][src.c]
        dst: Cell = self.grid[dst.r][dst.c]
        copy_action = Action(src, dst, action.player)
        return copy_action

    """    
        apply the given move
        @param move the move to apply
    """

    def apply_action(self, action: Action):
        # we store the copy move in the moves list not the given move
        action = self._validate_action(action)
        self.actions.append(action)
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        # if the move is king move
        if src.get_type() == Type.KING:
            self.move_like_king(action)
            return
        # this move isn't king move, so it's soldier move
        """
            we get the middle cell between src and dst, in case of WALK the
            middle cell will be either the src cell or dst cell, in case of EAT 
            the middle cell will be the eaten cell
        """
        middle_r = (src_r + dst_r) // 2
        middle_c = (src_c + dst_c) // 2
        middle: Cell = self.grid[middle_r][middle_c]
        # in case of EAT
        if middle != dst and middle != src and middle.piece is not None:
            #            copyAction.eat = deepcopy(middle.piece)
            action.capture = middle.piece
            middle.piece.dead = True
            # self.removePiece(middle.piece)
            middle.piece = None

        # removePiece(src)
        self.grid[src_r][src_c].piece.cell = dst
        self.grid[dst_r][dst_c].piece = self.grid[src_r][src_c].piece
        self.grid[src_r][src_c].piece = None
        # addPiece(dst.getPiece())
        # if a pawn reaches the end, it'll promoted to king
        if dst.get_color() == Color.WHITE and dst.r == 0:
            dst.set_type(Type.KING)
            action.promote = True
        if dst.get_color() == Color.BLACK and dst.r == 7:
            dst.set_type(Type.KING)
            action.promote = True
        #if action.capture is not None and self.can_capture(self.grid[dst_r][dst_c].piece):
         #   return

        #self.current_turn = 3 - self.current_turn

    # undo the last move
    def undo(self):
        action: Action = self.actions.pop()
        src = action.src
        dst = action.dst
        piece = action.capture
        if piece is not None:
            piece.cell.piece = piece
            piece.dead = False
        if dst.get_color() == Color.WHITE and dst.r == 0:
            dst.set_type(Type.PAWN)
        if dst.get_color() == Color.BLACK and dst.r == 9:
            dst.set_type(Type.PAWN)
        src.piece = dst.piece
        dst.piece = None
        src.piece.cell = src
