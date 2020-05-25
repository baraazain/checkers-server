from abc import ABC, abstractmethod
from random import randrange

from .game import Action


class Player(ABC):

    def __init__(self, _id, name, password):
        self.id = _id
        self.name = name
        self.password = password
        self.rate = 1000
        self.currentContest = []

    @abstractmethod
    def act(self, game) -> Action:
        pass
    
    def __eq__(self, other):
        if isinstance(other, Player):
            if other is self:
                return True
            if self.id == other.id:
                return True
        return False


class Human(Player, ABC):
    pass


class ConsolePlayer(Human):
    def __init__(self, _id, name, password):
        super().__init__(_id, name, password)

    def act(self, game):
        actions = game.get_all_possible_actions()
        size = len(actions)
        for idx, action in enumerate(actions):
            print(str(idx + 1) + "." + str(action))
        while True:
            choice = int(input('Enter your choice:'))
            if 0 > choice or size < choice:
                continue
            return actions[choice - 1]


class Agent(Player, ABC):
    pass


class RandomAgent(Agent):
    def __init__(self):
        super().__init__(None, "Random", None)

    def act(self, game):
        actions = game.get_all_possible_actions()
        return actions[randrange(0, len(actions))]


class MiniMaxAgent(Agent, ABC):
    def __init__(self, maximum_depth):
        super().__init__(None, "Max", None)
        self.maximum_depth = maximum_depth

    def max(self, alpha, beta, depth, game):
        if depth == self.maximum_depth or game.end():
            return self.evaluate(game), None
        return_action = None
        actions, states = game.get_all_possible_states()
        for action, state in zip(actions, states):
            value, _ = self.min(alpha, beta, depth + 1, state)
            if alpha < value:
                alpha = value
                return_action = action
            if alpha >= beta:
                return beta, None
        return alpha, return_action

    def min(self, alpha, beta, depth, game):
        if depth == self.maximum_depth or game.end():
            return self.evaluate(game), None
        return_action = None
        actions, states = game.get_all_possible_states()
        for action, state in zip(actions, states):
            value, _ = self.max(alpha, beta, depth + 1, state)
            if beta > value:
                beta = value
                return_action = action
            if alpha >= beta:
                return alpha, None
        return beta, return_action

    @abstractmethod
    def evaluate(self, game):
        pass

    def act(self, game):
        value, action = self.max(int(-1e9), int(1e9), 0, game)
        return action
