from abc import ABC, abstractmethod
from random import randrange
from copy import deepcopy
# because of circular in import Contest/Player U can't use from module import class style
# use this style then access the Contest class from the contest module
import model as md

from .game import Action


class Player(ABC):

    def __init__(self, _id, name, password, rate=1600, current_contests= []):
        self.id = _id
        self.name = name
        self.password = password
        self.rate = rate
        self.current_contests = current_contests

    @abstractmethod
    def act(self, game) -> Action:
        pass
    

    @classmethod
    def from_dict(cls, dictionary):
        dictionary=deepcopy(dictionary)
        contests = []
        
        for contest in dictionary['current_contests']:
          contests.append(md.contest.Contest.from_dict(contest))

        dictionary['current_contests'] = contests

        p = cls(None, None, None)

        p.__dict__ = dictionary

        return p

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def __init__(self, _id=None, name="Random", password=None, rate=1600, current_contests=[]):
        super().__init__(_id,name,password, rate, current_contests)

    def act(self, game):
        actions = game.get_all_possible_actions()
        return actions[randrange(0, len(actions))]


class MiniMaxAgent(Agent, ABC):
    def __init__(self, maximum_depth, _id=None, name="Max", password=None, rate=1600, current_contests=[]):
        super().__init__(_id,name, password, rate, current_contests)
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
