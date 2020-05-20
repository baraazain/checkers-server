from abc import ABC, abstractmethod
from copy import deepcopy

from .piece import *


class Mode:
    INTERNATIONAL = "INTERNATIONAL"
    TURKISH = "TURKISH"


class Action:

    def __init__(self, src, dst, player):
        self.id = -1
        self.src = src
        self.dst = dst
        self.player = player
        self.capture = None

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


class Game(ABC):

    @classmethod
    def build(cls, whitePieces, blackPieces, turn):
        return None

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
    def get_maximum_captures(self, piece, player):
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
    def get_all_possible_actions(self):
        pass

    def get_all_possible_states(self):
        states = []
        actions = self.get_all_possible_actions()
        for action in actions:
            new_state = deepcopy(self)
            new_state.apply_action(action)
            states.append(new_state)
        return actions, states

    @abstractmethod
    def correct_king_eat(self, action):
        pass

    @abstractmethod
    def move_like_king(self, action):
        pass

    @abstractmethod
    def correct_walk(self, action):
        pass

    @abstractmethod
    def correct_eat(self, action):
        pass

    @abstractmethod
    def is_legal_action(self, action):
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
            if piece.dead:
                white_dead_cnt += 1
        if white_dead_cnt == len(self.white_pieces):
            return 2
        for piece in self.black_pieces:
            if piece.dead:
                black_dead_cnt += 1
        if black_dead_cnt == len(self.black_pieces):
            return 1
        return 3

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

    @abstractmethod
    def undo(self):
        pass

    def end(self):
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

    def print_the_winner(self):
        winner = self.get_winner()
        if winner == 1:
            print("player #1 the winner")
        elif winner == 2:
            print("player #2 the winner")
        else:
            print("Draw -_-")

    def winner_rate(self, winner):
        if winner == 1:
            winnerRate = self.player1.getRate()
            opponentRate = self.player2.getRate()
            res = 1 + pow(10, 0.1 * (winnerRate - opponentRate) / 400)
            return 1 / res

        if winner == 2:
            winnerRate = self.player2.getRate()
            opponentRate = self.player1.getRate()
            res = 1 + pow(10, 0.1 * (winnerRate - opponentRate) / 400)
            return 1 / res

    @staticmethod
    def convert_rate(rate):
        if rate < 2100:
            return 32
        if 2200 <= rate < 2400:
            return 24
        return 16

    def outcome(self, playerNumber):
        if self.get_winner() == 0:
            return 0.5
        if self.get_winner() == playerNumber:
            return 1
        return 0

    def change_rate(self):
        self.player1.rate += Game.convert_rate(self.player1.getRate()) * (self.outcome(1) - self.winner_rate(1))
        self.player2.rate += Game.convert_rate(self.player2.getRate()) * (self.outcome(2) - self.winner_rate(2))
