import copy

from .action import Action
from .actors import Player
from .game import Game
from .grid import Grid
from .piece import *


class InternationalGame(Game):
    @classmethod
    def build(cls, white_pieces: list, black_pieces: list, turn: int, no_progress_count: int):
        game = cls(-1, None, None, None)
        game.white_pieces = copy.deepcopy(white_pieces)
        game.black_pieces = copy.deepcopy(black_pieces)
        game.current_turn = turn
        pieces = game.white_pieces + game.black_pieces
        for piece in pieces:
            if not piece.dead:
                game.grid[piece.cell.r][piece.cell.c].piece = piece
                piece.cell = game.grid[piece.cell.r][piece.cell.c]
        game.no_progress_count = no_progress_count
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
        self.promote = False

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
        if abs(src_r - dst_r) != abs(src_c - dst_c):
            return False
        dir_r = (dst_r - src_r) // abs(src_r - dst_r)
        dir_c = (dst_c - src_c) // abs(src_c - dst_c)
        cur_r = src_r + dir_r
        cur_c = src_c + dir_c
        while cur_r != dst_r:
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

    def correct_king_capture(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        if src.piece is None:
            return False, None
        if dst.piece is not None:
            return False, None
        if abs(src_r - dst_r) != abs(src_c - dst_c):
            return False, None
        dir_r = (dst_r - src_r) // abs(src_r - dst_r)
        dir_c = (dst_c - src_c) // abs(src_c - dst_c)
        cur_r = src_r + dir_r
        cur_c = src_c + dir_c
        cnt = 0
        piece = None
        while cur_r != dst_r:
            if self.grid[cur_r][cur_c].get_color() == src.get_color():
                return False, None
            if self.grid[cur_r][cur_c].piece is not None:
                cnt += 1
                piece = self.grid[cur_r][cur_c].piece
            cur_r += dir_r
            cur_c += dir_c
        if cnt == 1:
            for action in self.path:
                if action.capture == piece:
                    return False, None
            return True, piece
        else:
            return False, None

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
        Check if the move is correct pawn capture or not.
        @param move the move to check.
        @return true if correct pawn eat and false otherwise.
    """

    def correct_capture(self, action: Action):
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c
        if src.get_type() == Type.KING:
            return self.correct_king_capture(action)
        if src.piece is None:
            return False, None
        if dst.piece is not None:
            return False, None
        if abs(src_r - dst_r) != 2 or abs(src_c - dst_c) != 2:
            return False, None

        middle_r = (src_r + dst_r) // 2
        middle_c = (src_c + dst_c) // 2
        middle_cell = self.grid[middle_r][middle_c]
        if middle_cell.piece is None:
            return False, None
        if middle_cell.get_color() == src.get_color():
            return False, None

        for action in self.path:
            if action.capture == middle_cell.piece:
                return False, None
        return True, middle_cell.piece

    """
        Check if piece can walk primary diagonal.
        @param piece the piece to check.
        @return true if can walk primary and false otherwise.
    """

    def can_walk_primary(self, piece: Piece):
        src = piece.cell
        cur_r = src.r
        cur_c = src.c
        while cur_r > 0 and cur_c > 0:
            cur_r -= 1
            cur_c -= 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        cur_r = src.r
        cur_c = src.c
        while cur_r < 9 and cur_c < 9:
            cur_r += 1
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
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
        cur_r = src.r
        cur_c = src.c
        while cur_r < 9 and cur_c > 0:
            cur_r += 1
            cur_c -= 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            if self.correct_walk(action):
                return True
        cur_r = src.r
        cur_c = src.c
        while cur_r > 0 and cur_c < 9:
            cur_r -= 1
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
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
        cur_r = src.r
        cur_c = src.c
        while cur_r > 0 and cur_c > 0:
            cur_r -= 1
            cur_c -= 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            ans, _ = self.correct_capture(action)
            if ans:
                return True
        cur_r = src.r
        cur_c = src.c
        while cur_r < 9 and cur_c < 9:
            cur_r += 1
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            ans, _ = self.correct_capture(action)
            if ans:
                return True
        return False

    """
        Check if piece can eat secondary diagonal.
        @param piece the piece to check.
        @return true if can eat secondary and false otherwise.
    """

    def can_capture_secondary(self, piece: Piece):
        src = piece.cell
        cur_r = src.r
        cur_c = src.c
        while cur_r < 9 and cur_c > 0:
            cur_r += 1
            cur_c -= 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            ans, _ = self.correct_capture(action)
            if ans:
                return True
        cur_r = src.r
        cur_c = src.c
        while cur_r > 0 and cur_c < 9:
            cur_r -= 1
            cur_c += 1
            dst = self.grid[cur_r][cur_c]
            action = Action(src, dst, None)
            ans, _ = self.correct_capture(action)
            if ans:
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
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_primary_walks(self, piece: Piece, current_player: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, c)
        st_r = r - mn
        st_c = c - mn
        # (st_r, st_c) represents the first cell in the primary diagonal
        actions = []
        while st_r < 10 and st_c < 10:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_walk(action):
                actions.append(action)
            # next cell in the primary diagonal is (i+1, j+1)
            st_r += 1
            st_c += 1
        return actions

    """
        calc all possible walks in the secondary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_secondary_walks(self, piece: Piece, current_player: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, 9 - c)
        st_r = r - mn
        st_c = c + mn
        # (st_r, st_c) represents the first cell in the secondary diagonal
        actions = []
        while st_r < 10 and st_c >= 0:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            if self.correct_walk(action):
                actions.append(action)
            # next cell in the secondary diagonal is (i+1, j-1)
            st_r += 1
            st_c -= 1
        return actions

    """
        calc all possible eats in the primary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_primary_captures(self, piece: Piece, current_player: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, c)
        st_r = r - mn
        st_c = c - mn
        actions = []
        while st_r < 10 and st_c < 10:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            ans, piece = self.correct_capture(action)
            if ans:
                action.capture = piece
                actions.append(action)
            st_r += 1
            st_c += 1
        return actions

    """
        calc all possible eats in the secondary diagonal for a given
        piece for a given player
        @param piece the given piece
        @param cur_rentPlayer the given player
        @return List of moves
    """

    def get_all_possible_secondary_captures(self, piece: Piece, current_player: Player):
        src = piece.cell
        r = src.r
        c = src.c
        mn = min(r, 9 - c)
        st_r = r - mn
        st_c = c + mn
        actions = []
        while st_r < 10 and st_c >= 0:
            dst = self.grid[st_r][st_c]
            action = Action(src, dst, current_player)
            ans, piece = self.correct_capture(action)
            if ans:
                action.capture = piece
                actions.append(action)
            st_r += 1
            st_c -= 1
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

    # @return all possible walks from the cur_rent state
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

        captures = self.get_all_possible_primary_captures(piece, player)
        captures = captures + self.get_all_possible_secondary_captures(piece, player)

        for capture in captures:
            self.path.append(capture)
            self.apply_action(capture)
            self.get_maximum_captures(piece, player, 1 + cur_value)
            self.undo()
            self.path.pop()

        return self.mx, self.paths

    # @return all possible eats from current states
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
        pass

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
        if self.correct_capture(action) or self.correct_walk(action):
            return True
        return False

    def apply_turn(self, actions: list):
        size = len(actions)

        validated_actions = []
        for action in actions:
            validated_actions.append(self._validate_action(action))

        for idx, action in enumerate(validated_actions):
            if idx == size - 1:
                self.promote = True
            self.apply_action(action)

        for action in validated_actions:
            if action.capture is not None:
                action.capture.dead = True
                action.capture.cell.piece = None

        self.promote = False
        self.current_turn = 3 - self.current_turn

    """    
        apply the given move
        @param move the move to apply
    """

    def apply_action(self, action: Action):
        self.no_progress -= 1

        # we store the copy move in the moves list not the given move
        self.actions.append(action)
        src: Cell = action.src
        dst: Cell = action.dst
        src_r = src.r
        src_c = src.c
        dst_r = dst.r
        dst_c = dst.c

        # in case of EAT
        if action.capture is not None:
            self.no_progress = self.NO_PROGRESS_LIMIT

        self.grid[src_r][src_c].piece.cell = dst
        self.grid[dst_r][dst_c].piece = self.grid[src_r][src_c].piece
        self.grid[src_r][src_c].piece = None

        if self.promote:
            # if a pawn stop at the end, it'll promoted to king
            if dst.get_color() == Color.WHITE and dst.r == 0:
                dst.set_type(Type.KING)
                action.promote = True
                self.no_progress = self.NO_PROGRESS_LIMIT

            if dst.get_color() == Color.BLACK and dst.r == 9:
                dst.set_type(Type.KING)
                action.promote = True
                self.no_progress = self.NO_PROGRESS_LIMIT

    # undo the last move
    def undo(self):
        if self.actions:
            action: Action = self.actions.pop()
            src = action.src
            dst = action.dst

            if action.promote:
                dst.set_type(Type.PAWN)

            self.no_progress = action.no_progress_count
            src.piece = dst.piece
            dst.piece = None
            src.piece.cell = src
