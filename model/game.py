from copy import deepcopy

from .grid import Grid
from .piece import *
from abc import ABC, abstractmethod


class Mode:
    INTERNATIONAL = "INTERNATIONAL"
    TURKISH = "TURKISH"


class Action:

    def __init__(self, source, destination, player):
        self.id = -1
        self.src = source
        self.dst = destination
        self.player = player
        self.eat = None

    def isEat(self):
        return self.eat is not None

    def __str__(self):
        ret = "(" + str(self.src.r + 1) + ',' + str(self.src.c + 1) + ")"
        ret += "------->>>"
        ret += "(" + str(self.dst.r + 1) + "," + str(self.dst.c + 1) + ")"
        return ret
    
    def __eq__(self, other):
        if isinstance(other, Action):
            if self.src == other.src and self.dst == other.dst:
                if self.player == other.player and self.eat == other.eat:
                    return True
        return False;


class Game(ABC):
    
    @classmethod
    def build(cls, whitePieces, blackPieces, turn):
        return None

    def __init__(self, id_key, player1, player2, date):
        self.id = id_key
        self.player1 = player1
        self.player2 = player2
        self.date = date

        self.grid = None
        self.actions = []
        self.blackPieces = []
        self.whitePieces = []
        self.currentTurn = 1

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def canWalk(self, piece):
        pass

    @abstractmethod
    def canEat(self, piece):
        pass

    @abstractmethod
    def canMove(self, piece):
        pass

    @abstractmethod
    def getMaximumEat(self):
        pass

    @abstractmethod
    def correctKingWalk(self, action):
        pass

    @abstractmethod
    def getAllPossibleWalks(self):
        pass

    @abstractmethod
    def getAllPossibleEats(self):
        pass

    @abstractmethod
    def getAllPossibleActions(self):
        pass

    def getAllPossibleStates(self):
        states = []
        actions = self.getAllPossibleActions()
        for action in actions:
            new_state = deepcopy(self)
            new_state.applyAction(action)
            states.append(new_state)
        return actions, states

    @abstractmethod
    def correctKingEat(self, action):
        pass

    @abstractmethod
    def moveLikeKing(self, action):
        pass

    @abstractmethod
    def correctWalk(self, action):
        pass

    @abstractmethod
    def correctEat(self, action):
        pass

    @abstractmethod
    def isLegalAction(self, action):
        pass

    @abstractmethod
    def applyAction(self, action):
        pass

    def getCurrentPlayer(self):
        return self.player1 if self.currentTurn == 1 else self.player2

    """
        Add piece to whitePieces array or blackPieces according to its
        content.
        @param piece the cell which contains the piece to add.
    """

    def addPiece(self, piece: Piece):
        if piece.color == Color.BLACK:
            self.blackPieces.append(piece)
        if piece.color == Color.WHITE:
            self.whitePieces.append(piece)

    """
        remove piece from whitePieces array or blackPieces according to its
        content.
        @param cell the cell which contains the piece to remove.
    """

    def removePiece(self, piece: Piece):
        if piece.color == Color.WHITE:
            self.whitePieces.remove(piece)
        if piece.color == Color.BLACK:
            self.blackPieces.remove(piece)

    # Start a new game
    def startGame(self):
        self.init()
        while not self.end():
            self.playTurn()
        print(self.grid)

    # return the winner
    def getWinner(self):
        winner = 3
        if len(self.whitePieces) != 0:
            winner -= 2
        if len(self.blackPieces) != 0:
            winner -= 1
        return winner

    """
        organize the turns, get the move from the white or black player
        (depending on turn)
    """

    def playTurn(self):
        if self.currentTurn == 1:
            # while True:
            move = self.player1.act(self)
            # if acceptMove(move):
            self.applyAction(move)
            #    break
            while self.actions[len(self.actions) - 1].isEat() \
                    and self.canEat(self.actions[len(self.actions) - 1].distination):
                self.applyAction(self.player1.act(self))
        else:
            # while True:
            move = self.player2.act(self)
            #      if acceptMove(move):
            self.applyAction(move)
            #       break
            while self.actions[len(self.actions) - 1].isEat() \
                    and self.canEat(self.actions[len(self.actions) - 1].distination):
                self.applyAction(self.player2.act(self))
        #self.currentTurn = 3 - self.currentTurn

    @abstractmethod
    def undo(self):
        pass

    def end(self):
        if len(self.blackPieces) == 0 or len(self.whitePieces) == 0:
            return True
        return len(self.getAllPossibleActions()) == 0

    def printTheWinner(self):
        winner = self.getWinner()
        if winner == 1:
            print("player #1 the winner")
        elif winner == 2:
            print("player #2 the winner")
        else:
            print("Draw -_-")

    def winnerRate(self, winner):
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
    def convertRate(rate):
        if rate < 2100:
            return 32
        if 2200 <= rate < 2400:
            return 24
        return 16

    def outcome(self, playerNumber):
        if self.getWinner() == 0:
            return 0.5
        if self.getWinner() == playerNumber:
            return 1
        return 0

    def changeRate(self):
        self.player1.rate += Game.convertRate(self.player1.getRate()) * (self.outcome(1) - self.winnerRate(1))
        self.player2.rate += Game.convertRate(self.player2.getRate()) * (self.outcome(2) - self.winnerRate(2))
