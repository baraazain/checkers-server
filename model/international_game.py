from copy import deepcopy

from .actors import Player
from .game import Game, Action
from .grid import Grid
from .piece import *


class InternationalGame(Game):
    @classmethod
    def build(cls, whitePieces: list, blackPieces: list, turn: int):
        game = cls(-1, None, None, None)
        game.white_pieces = deepcopy(whitePieces)
        game.black_pieces = deepcopy(blackPieces)
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
            for i in range(10):
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
        self.grid = Grid(10, 10)

    # initialize the grid and add pieces to their respective array
    def init(self):
        for i in range(0, 4):
            x = 1 - (i % 2)
            for j in range(x, 10, 2):
                piece = Piece(self.grid[i][j], Type.PAWN, Color.BLACK)
                self.grid[i][j].piece = piece
                self.black_pieces.append(piece)
        for i in range(6, 10, 1):
            x = 1 - (i % 2)
            for j in range(x, 10, 2):
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
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        if src.get_type() != Type.KING:
            return False
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if abs(srcR - dstR) != abs(srcC - dstC):
            return False
        dirR = (dstR - srcR) // abs(srcR - dstR)
        dirC = (dstC - srcC) // abs(srcC - dstC)
        curR = srcR + dirR
        curC = srcC + dirC
        while curR != dstR:
            if self.grid[curR][curC].piece is not None:
                return False
            curR += dirR
            curC += dirC
        return True

    """
        Check if the move is correct king eat or not.
        @param move the move to check.
        @return true if correct king eat and false otherwise.
    """

    def correct_king_eat(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if abs(srcR - dstR) != abs(srcC - dstC):
            return False
        dirR = (dstR - srcR) // abs(srcR - dstR)
        dirC = (dstC - srcC) // abs(srcC - dstC)
        curR = srcR + dirR
        curC = srcC + dirC
        cnt = 0
        while curR != dstR:
            if self.grid[curR][curC].get_color() == src.get_color():
                return False
            if self.grid[curR][curC].piece is not None:
                cnt += 1
            curR += dirR
            curC += dirC
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
        elif src.get_color() == Color.WHITE:
            ar = [-1, -1]
            for i in range(0, 2, 1):
                nr = r + ar[i]
                nc = c + ac[i]
                if nr == dst.r and nc == dst.c:
                    return True
        elif src.get_color() == Color.BLACK:
            ar = [1, 1]
            for i in range(0, 2, 1):
                nr = r + ar[i]
                nc = c + ac[i]
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
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        if src.get_type() == Type.KING:
            return self.correct_king_eat(action)
        if src.piece is None:
            return False
        if dst.piece is not None:
            return False
        if abs(srcR - dstR) != 2 or abs(srcC - dstC) != 2:
            return False
        middleR = (srcR + dstR) // 2
        middleC = (srcC + dstC) // 2
        middleCell = self.grid[middleR][middleC]
        if middleCell.piece is None:
            return False
        if middleCell.get_color() == src.get_color():
            return False
        return True

    """
        Check if piece can walk primary diagonal.
        @param piece the piece to check.
        @return true if can walk primary and false otherwise.
    """

    def can_walk_primary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR > 0 and curC > 0:
            curR -= 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        curR = src.r
        curC = src.c
        while curR < 9 and curC < 9:
            curR += 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        return False

    """
        Check if piece can walk secondary diagonal.
        @param piece the piece to check.
        @return true if can walk secondary and false otherwise.
    """

    def can_walk_secondary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR < 9 and curC > 0:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        curR = src.r
        curC = src.c
        while curR > 0 and curC < 9:
            curR -= 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        return False

    """
        Check if piece can eat primary diagonal.
        @param piece the piece to check.
        @return true if can eat primary and false otherwise.
    """

    def can_capture_primary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR > 0 and curC > 0:
            curR -= 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        curR = src.r
        curC = src.c
        while curR < 9 and curC < 9:
            curR += 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        return False

    """
        Check if piece can eat secondary diagonal.
        @param piece the piece to check.
        @return true if can eat secondary and false otherwise.
    """

    def can_capture_secondary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR < 9 and curC > 0:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        curR = src.r
        curC = src.c
        while curR > 0 and curC < 9:
            curR -= 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correct_eat(action):
                return True
        return False

    def can_walk(self, piece):
        return self.can_walk_primary(piece) or self.can_walk_secondary(piece)

    def can_capture(self, piece):
        return self.can_capture_primary(piece) or self.can_capture_secondary(piece)

    def can_move(self, piece):
        return self.can_walk(piece) or self.can_capture(piece)

    """
        calc all possible walks in the primary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param currentPlayer the given player
        @return List of moves
    """

    def get_all_possible_primary_walks(self, piece: Piece, currentPlayer: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, c)
        stR = r - mn
        stC = c - mn
        # (stR, stC) represents the first cell in the primary diagonal
        actions = []
        while stR < 10 and stC < 10:
            dst = self.grid[stR][stC]
            action = Action(src, dst, currentPlayer)
            if self.correct_walk(action):
                actions.append(action)
            # next cell in the primary diagonal is (i+1, j+1)
            stR += 1
            stC += 1
        return actions

    """
        calc all possible walks in the secondary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param currentPlayer the given player
        @return List of moves
    """

    def get_all_possible_secondary_walks(self, piece: Piece, currentPlayer: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, 9 - c)
        stR = r - mn
        stC = c + mn
        # (stR, stC) represents the first cell in the secondary diagonal
        actions = []
        while stR < 10 and stC >= 0:
            dst = self.grid[stR][stC]
            action = Action(src, dst, currentPlayer)
            if self.correct_walk(action):
                actions.append(action)
            # next cell in the secondary diagonal is (i+1, j-1)
            stR += 1
            stC -= 1
        return actions

    """
        calc all possible eats in the primary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param currentPlayer the given player
        @return List of moves
    """

    def get_all_possible_primary_captures(self, piece: Piece, currentPlayer: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, c)
        stR = r - mn
        stC = c - mn
        actions = []
        while stR < 10 and stC < 10:
            dst = self.grid[stR][stC]
            action = Action(src, dst, currentPlayer)
            if self.correct_eat(action):
                actions.append(action)
            stR += 1
            stC += 1
        return actions

    """
        calc all possible eats in the secondary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param currentPlayer the given player
        @return List of moves
    """

    def get_all_possible_secondary_captures(self, piece: Piece, currentPlayer: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, 9 - c)
        stR = r - mn
        stC = c + mn
        actions = []
        while stR < 10 and stC >= 0:
            dst = self.grid[stR][stC]
            action = Action(src, dst, currentPlayer)
            if self.correct_eat(action):
                actions.append(action)
            stR += 1
            stC -= 1
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
                    actions.extend(self.get_all_possible_primary_walks(piece, self.player1))
                    actions.extend(self.get_all_possible_secondary_walks(piece, self.player1))
        else:
            # iterate over all black pieces and get the moves for this pieces
            for piece in self.black_pieces:
                if not piece.dead:
                    actions.extend(self.get_all_possible_primary_walks(piece, self.player2))
                    actions.extend(self.get_all_possible_secondary_walks(piece, self.player2))
        return actions

    def get_maximum_captures(self, piece, player):
        if not self.can_capture(piece):
            self.current_turn = 3 - self.current_turn
            return 0, None
        captures = self.get_all_possible_primary_captures(piece, player)
        captures = captures + self.get_all_possible_secondary_captures(piece, player)
        mx = 0
        actions = []
        for capture in captures:
            self.apply_action(capture)
            value, _ = self.get_maximum_captures(piece, player)
            
            if mx < value + 1:
                mx = value + 1
                actions.clear()
                actions.append(capture)
            
            if mx == value:
                action.append(capture)

            self.undo()

        return mx, actions

    # @return all possible eats from current states
    def get_all_possible_captures(self):
        actions_value_pairs = []
        if self.current_turn == 1:
            # iterate over all white pieces and get the moves from the pieces
            for piece in self.white_pieces:
                if not piece.dead:
                    if self.can_capture(piece):
                        actions_value_pairs.append(self.get_maximum_captures(piece, self.player1))
        else:
            # iterate over all black pieces and get the moves from this pieces
            for piece in self.black_pieces:
                if not piece.dead:
                    if self.can_capture(piece):
                        actions_value_pairs.append(self.get_maximum_captures(piece, self.player2))

        mx = 0
        for value, _ in actions_value_pairs:
            mx = max(mx, value)
        
        captures = []
        for value, actions_list in actions_value_pairs:
            if value == mx:
                captures.extend(actions_list)

        return captures

    """      
        implements king's move
        @param move the king's move
    """

    def move_like_king(self, action: Action):
        srcR = action.src.r
        srcC = action.src.c
        dstR = action.dst.r
        dstC = action.dst.c
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
        dirR = (dstR - srcR) // abs(dstR - srcR)
        dirC = (dstC - srcC) // abs(dstC - srcC)
        curR = srcR
        curC = srcC
        while curR != dstR:
            cur: Cell = self.grid[curR][curC]
            """ 
                if we get reach to non-empty piece, so we need to erase it from
                the board (eat case)
            """
            if cur.piece is not None:
                action.capture = cur.piece
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

    def is_legal_action(self, action: Action):
        r = action.src.r
        c = action.src.c
        # Wrong turn
        if self.current_turn == 1 and self.grid[r][c].get_color() != Color.WHITE:
            return False
        if self.current_turn == 2 and self.grid[r][c].get_color() != Color.BLACK:
            return False
        action = self._validateAction(action)
        if self.correct_eat(action) or self.correct_walk(action):
            return True
        return False

    def _validateAction(self, action):
        src: Cell = action.src
        dst: Cell = action.dst
        src: Cell = self.grid[src.r][src.c]
        dst: Cell = self.grid[dst.r][dst.c]
        copyAction = Action(src, dst, action.player)
        return copyAction

    """    
        apply the given move
        @param move the move to apply
    """

    def apply_action(self, action: Action):
        # we store the copy move in the moves list not the given move
        action = self._validateAction(action)
        self.actions.append(action)
        src: Cell = action.src
        dst: Cell = action.dst
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
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
        middleR = (srcR + dstR) // 2
        middleC = (srcC + dstC) // 2
        middle: Cell = self.grid[middleR][middleC]
        # in case of EAT
        if middle != dst and middle != src and middle.piece is not None:
            #            copyAction.eat = deepcopy(middle.piece)
            action.capture = middle.piece
            middle.piece.dead = True
            # self.removePiece(middle.piece)
            middle.piece = None

        # removePiece(src)
        self.grid[srcR][srcC].piece.cell = dst
        self.grid[dstR][dstC].piece = self.grid[srcR][srcC].piece
        self.grid[srcR][srcC].piece = None
        # addPiece(dst.getPiece())
        # if a pawn reaches the end, it'll promoted to king
        if dst.get_color() == Color.WHITE and dst.r == 0:
            dst.set_type(Type.KING)
        if dst.get_color() == Color.BLACK and dst.r == 9:
            dst.set_type(Type.KING)
        if action.capture is not None and self.can_capture(self.grid[dstR][dstC].piece):
            return
        self.current_turn = 3 - self.current_turn

    # undo the last move
    def undo(self):
        action: Action = self.actions.pop()
        src = action.src
        dst = action.dst
        piece = action.capture
        if piece is not None:
            piece.cell.piece = piece
            piece.dead = False
        src.piece = dst.piece
        dst.piece = None
        src.piece.cell = src
