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


