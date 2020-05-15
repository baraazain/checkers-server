from .Game import Game, Action
from .Piece import *
from .Grid import Cell
from .Actors import Player
from copy import deepcopy


class InternationalGame(Game):
    @classmethod
    def build(cls, whitePieces: list, blackPieces:list, turn: int):
        game = cls(-1, None, None, None)
        game.whitePieces = deepcopy(whitePieces)
        game.blackPieces = deepcopy(blackPieces)
        game.currentTurn = turn
        pieces = game.whitePieces + game.blackPieces
        for piece in pieces:
            game.grid[piece.cell.r][piece.cell.c] = piece
        return game

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # initialize the grid and add pieces to their respective array
    def init(self):
        for i in range(0, 4):
            x = 1 - (i % 2)
            for j in range(x, 10, 2):
                piece = Piece(self.grid[i][j], Type.PAWN, Color.BLACK)
                self.grid[i][j].piece = piece
                self.blackPieces.append(piece)
        for i in range(6, 10, 1):
            x = 1 - (i % 2)
            for j in range(x, 10, 2):
                piece = Piece(self.grid[i][j], Type.PAWN, Color.WHITE)
                self.grid[i][j].piece = piece
                self.whitePieces.append(piece)

    """
        Check if the move is correct king walk or not.
        @param move the move to check.
        @return true if correct king walk and false otherwise.
    """

    def correctKingWalk(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        if src.getType() != Type.KING:
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

    def correctKingEat(self, action: Action):
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
            if self.grid[curR][curC].getColor() == src.getColor():
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

    def correctWalk(self, action: Action):
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
        if src.getType() == Type.KING:
            return self.correctKingWalk(action)
        elif src.getColor() == Color.WHITE:
            ar = [-1, -1]
            for i in range(0, 2, 1):
                nr = r + ar[i]
                nc = c + ac[i]
                if nr == dst.r and nc == dst.c:
                    return True
        elif src.getColor() == Color.BLACK:
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

    def correctEat(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        if src.getType() == Type.KING:
            return self.correctKingEat(action)
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
        if middleCell.getColor() == src.getColor():
            return False
        return True

    """
        Check if piece can walk primary diagonal.
        @param piece the piece to check.
        @return true if can walk primary and false otherwise.
    """

    def canWalkPrimary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR > 0 and curC > 0:
            curR -= 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctWalk(action):
                return True
        curR = src.r
        curC = src.c
        while curR < 9 and curC < 9:
            curR += 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctWalk(action):
                return True
        return False

    """
        Check if piece can walk secondary diagonal.
        @param piece the piece to check.
        @return true if can walk secondary and false otherwise.
    """

    def canWalkSecondary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR < 9 and curC > 0:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctWalk(action):
                return True
        curR = src.getR()
        curC = src.getC()
        while curR > 0 and curC < 9:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctWalk(action):
                return True
        return False

    """
        Check if piece can eat primary diagonal.
        @param piece the piece to check.
        @return true if can eat primary and false otherwise.
    """

    def canEatPrimary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR > 0 and curC > 0:
            curR -= 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctEat(action):
                return True
        curR = src.r
        curC = src.c
        while curR < 9 and curC < 9:
            curR += 1
            curC += 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctEat(action):
                return True
        return False

    """
        Check if piece can eat secondary diagonal.
        @param piece the piece to check.
        @return true if can eat secondary and false otherwise.
    """

    def canEatSecondary(self, piece: Piece):
        src = piece.cell
        curR = src.r
        curC = src.c
        while curR < 9 and curC > 0:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctEat(action):
                return True
        curR = src.r
        curC = src.c
        while curR > 0 and curC < 9:
            curR += 1
            curC -= 1
            dst = self.grid[curR][curC]
            action = Action(src, dst, None)
            if self.correctEat(action):
                return True
        return False

    def canWalk(self, piece):
        return self.canWalkPrimary(piece) or self.canWalkSecondary(piece)

    def canEat(self, piece):
        return self.canEatPrimary(piece) or self.canEatSecondary(piece)

    def canMove(self, piece):
        return self.canWalk(piece) or self.canEat(piece)

    """
        calc all possible walks in the primary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param currentPlayer the given player
        @return List of moves
    """

    def getAllPossiblePrimaryWalks(self, piece: Piece, currentPlayer: Player):
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
            if self.correctWalk(action):
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

    def getAllPossibleSecondaryWalks(self, piece: Piece, currentPlayer: Player):
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
            if self.correctWalk(action):
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

    def getAllPossiblePrimaryEats(self, piece: Piece, currentPlayer: Player):
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
            if self.correctEat(action):
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

    def getAllPossibleSecondaryEats(self, piece: Piece, currentPlayer: Player):
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
            if self.correctEat(action):
                actions.append(action)
            stR += 1
            stC -= 1
        return actions

    """     
        @param src
        @return all possible moves starting from given cell
    """

    def getAllPossibleActions(self):
        actions = self.getAllPossibleEats()
        if len(actions) == 0:
            actions = self.getAllPossibleWalks()
        return actions

    # @return all possible walks from the current state
    def getAllPossibleWalks(self):
        actions = []
        print(self.currentTurn)
        if self.currentTurn == 1:
            # iterate over all white pieces and get the moves from the pieces
            for piece in self.whitePieces:
                actions.extend(self.getAllPossiblePrimaryWalks(piece, self.player1))
                actions.extend(self.getAllPossibleSecondaryWalks(piece, self.player1))
        else:
            # iterate over all black pieces and get the moves for this pieces
            for piece in reversed(self.blackPieces):
                actions.extend(self.getAllPossiblePrimaryWalks(piece, self.player2))
                actions.extend(self.getAllPossibleSecondaryWalks(piece, self.player2))
            print(len(actions))
        return actions

    # @return all possible eats from current states
    def getAllPossibleEats(self):
        actions = []
        if self.currentTurn == 1:
            # iterate over all white pieces and get the moves from the pieces
            for piece in self.whitePieces:
                actions.extend(self.getAllPossiblePrimaryEats(piece, self.player1))
                actions.extend(self.getAllPossibleSecondaryEats(piece, self.player1))
        else:
            # iterate over all black pieces and get the moves from this pieces
            for piece in self.blackPieces:
                actions.extend(self.getAllPossiblePrimaryEats(piece, self.player2))
                actions.extend(self.getAllPossibleSecondaryEats(piece, self.player2))
        return actions

    """      
        implements king's move
        @param move the king's move
    """

    def moveLikeKing(self, action: Action):
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
                action.eat = deepcopy(cur.piece)
                self.removePiece(cur.piece)
                cur.piece = None
                break
            curR += dirR
            curC += dirC
        if action.eat is None:
            self.currentTurn = 3 - self.currentTurn
        self.actions.append(action)

    """     
        @param move the move needs to implement
        @return if the given move can be implemented or not
    """

    def isLegalAction(self, action: Action):
        r = action.src.r
        c = action.src.c
        # Wrong turn
        if self.currentTurn == 1 and self.grid[r][c].getColor() != Color.WHITE:
            return False
        if self.currentTurn == 2 and self.grid[r][c].getColor() != Color.BLACK:
            return False
        actions = self.getAllPossibleActions()
        # if the move exists in allPossibleMoves, then it can be implemented
        return action in actions

    """    
        apply the given move
        @param move the move to apply
    """

    def getMaximumEat(self):
        pass

    def applyAction(self, action: Action):
        # we store the copy move in the moves list not the given move
        copyAction = deepcopy(action)
        self.actions.append(copyAction)
        src: Cell = action.src
        dst: Cell = action.dst
        srcR = src.r
        srcC = src.c
        dstR = dst.r
        dstC = dst.c
        typ = src.getType()
        # if the move is king move
        if typ == Type.KING:
            self.moveLikeKing(action)
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
            copyAction.eat = deepcopy(middle.piece)
            action.eat = deepcopy(middle.piece)
            self.removePiece(middle.piece)
            middle.piece = None
        # removePiece(src)
        self.grid[srcR][srcC].piece.cell = dst
        self.grid[dstR][dstC].piece = self.grid[srcR][srcC].piece
        self.grid[srcR][srcC].piece = None
        # addPiece(dst.getPiece())
        # if a pawn reaches the end, it'll promoted to king
        if dst.getColor() == Color.WHITE and dst.r == 0:
            dst.setType(Type.KING)
        if dst.getColor() == Color.BLACK and dst.r == 9:
            dst.setType(Type.KING)
        if action.eat is None:
            self.currentTurn = 3 - self.currentTurn

    # undo the last move
    def undo(self):  # need debug what if eat is None?!
        """action: Action = self.actions.get(len(self.actions) - 1)
        src = action.source
        dst = action.destination
        piece = action.getEat()
        piece.getCell().setPiece(piece)
        src.setPiece(dst.getPiece())
        dst.setPiece(Piece(dst, Type.PAWN, Color.EMPTY))
        src.getPiece().setCell(src)
        """
        pass
