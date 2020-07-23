from abc import ABC, abstractmethod
from copy import deepcopy

from .action import Action
from .actors import Player
from .piece import *

# Constants
MAXIMIZER = 1


class Mode:
    INTERNATIONAL = "INTERNATIONAL"
    TURKISH = "TURKISH"


class Level:
    HUMAN = "HUMAN"
    DUMMY = "DUMMY"
    ALPHA_BETA = "ALPHA_BETA"
    MONTE_CARLO = "MONTE_CARLO"
    ALPHA_ZERO = "ALPHA_ZERO"


class GameInfo:
    def __init__(self, mode, level):
        self.mode = mode
        self.level = level

    @classmethod
    def from_dict(cls, data):
        return GameInfo(**data)


class Game(ABC):
    NO_PROGRESS_LIMIT = 16

    @classmethod
    @abstractmethod
    def build(cls, whitePieces, blackPieces, turn, no_progress_count):
        pass

    def __init__(self, _id, player1, player2, date):
        self.id = _id
        self.player1 = player1
        self.player2 = player2
        self.date = date

        self.grid = None
        self.actions = []
        self.black_pieces = []
        self.white_pieces = []
        self.current_turn = 1
        self.paths = []
        self.path = []
        self.mx = 0
        self.no_progress = Game.NO_PROGRESS_LIMIT
        self.mode = None

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def can_walk(self, piece):
        pass

    @abstractmethod
    def can_capture(self, piece):
        pass

    @abstractmethod
    def can_move(self, piece):
        pass

    @abstractmethod
    def get_maximum_captures(self, piece, player, turn):
        pass

    @abstractmethod
    def correct_king_walk(self, action):
        pass

    @abstractmethod
    def get_all_possible_walks(self):
        pass

    @abstractmethod
    def get_all_possible_captures(self):
        pass

    @abstractmethod
    def get_all_possible_paths(self):
        pass

    def get_all_possible_states(self):
        states = []
        paths = self.get_all_possible_paths()
        for path in paths:
            new_state = deepcopy(self)
            new_state.apply_turn(path)
            states.append(new_state)
        return paths, states

    @abstractmethod
    def correct_king_capture(self, action):
        pass

    @abstractmethod
    def move_like_king(self, action):
        pass

    @abstractmethod
    def correct_walk(self, action):
        pass

    @abstractmethod
    def correct_capture(self, action):
        pass

    @abstractmethod
    def is_legal_action(self, action):
        pass

    @abstractmethod
    def apply_turn(self, actions: list):
        pass

    @abstractmethod
    def apply_action(self, action):
        pass

    def get_current_player(self):
        return self.player1 if self.current_turn == 1 else self.player2

    """
        Add piece to whitePieces array or blackPieces according to its
        content.
        @param piece the cell which contains the piece to add.
    """

    def add_piece(self, piece: Piece):
        if piece.color == Color.BLACK:
            self.black_pieces.append(piece)
        if piece.color == Color.WHITE:
            self.white_pieces.append(piece)

    """
        remove piece from whitePieces array or blackPieces according to its
        content.
        @param cell the cell which contains the piece to remove.
    """

    def remove_piece(self, piece: Piece):
        if piece.color == Color.WHITE:
            self.white_pieces.remove(piece)
        if piece.color == Color.BLACK:
            self.black_pieces.remove(piece)

    # Start a new game
    def start_game(self):
        self.init()
        while not self.end():
            self.play_turn()
        print(self.grid)

    # return the winner
    def get_winner(self):
        white_dead_cnt = 0
        black_dead_cnt = 0
        for piece in self.white_pieces:
            if piece.dead or not self.can_move(piece):
                white_dead_cnt += 1
        if white_dead_cnt == len(self.white_pieces):
            return 2
        for piece in self.black_pieces:
            if piece.dead or not self.can_move(piece):
                black_dead_cnt += 1
        if black_dead_cnt == len(self.black_pieces):
            return 1
        return 0

    def get_loser(self):
        white_dead_cnt = 0
        black_dead_cnt = 0
        for piece in self.white_pieces:
            if piece.dead or not self.can_move(piece):
                white_dead_cnt += 1
        if white_dead_cnt == len(self.white_pieces):
            return 1
        for piece in self.black_pieces:
            if piece.dead or not self.can_move(piece):
                black_dead_cnt += 1
        if black_dead_cnt == len(self.black_pieces):
            return 2
        return 0

    """
        organize the turns, get the move from the white or black player
        (depending on turn)
    """

    def play_turn(self):
        if self.current_turn == 1:
            # while True:
            move = self.player1.act(self)
            # if acceptMove(move):
            self.apply_action(move)
            #    break
            while self.actions[len(self.actions) - 1].is_capture() \
                    and self.can_capture(self.actions[len(self.actions) - 1].distination):
                self.apply_action(self.player1.act(self))
        else:
            # while True:
            move = self.player2.act(self)
            #      if acceptMove(move):
            self.apply_action(move)
            #       break
            while self.actions[len(self.actions) - 1].is_capture() \
                    and self.can_capture(self.actions[len(self.actions) - 1].distination):
                self.apply_action(self.player2.act(self))
        # self.currentTurn = 3 - self.currentTurn

    def end(self):
        if self.no_progress <= 0:
            return True
        if self.current_turn == 1:
            for piece in self.white_pieces:
                if not piece.dead:
                    if self.can_move(piece):
                        return False
        else:
            for piece in self.black_pieces:
                if not piece.dead:
                    if self.can_move(piece):
                        return False
        return True

    def get_the_winner(self):
        winner = self.get_winner()
        if winner == 1:
            return self.player1
        elif winner == 2:
            return self.player2
        else:
            return None

    def validate_action(self, action):
        src: Cell = action.src
        dst: Cell = action.dst
        src: Cell = self.grid[src.r][src.c]
        dst: Cell = self.grid[dst.r][dst.c]
        copy_action = Action(src, dst, action.player)
        copy_action.no_progress_count = self.no_progress
        if action.capture:
            capture_cell = action.capture.cell
            copy_action.capture = self.grid[capture_cell.r][capture_cell.c].piece
        return copy_action

    @abstractmethod
    def undo(self):
        pass
