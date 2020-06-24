from abc import ABC, abstractmethod
from .game import Action


class Player(ABC):

    def __init__(self, _id, name, password, rate=1600, current_contests=[], finish_contest=[], games_id_saved=[]):
        self.id = _id
        self.name = name
        self.password = password
        self.rate = rate
        self.current_contests = current_contests
        self.finish_contest=finish_contest
        self.games_id_saved=games_id_saved

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

    def on_update(self, action):
        pass

    def on_start(self, game):
        pass


class Human(Player, ABC):
    pass

class RemotePlayer(Human):
    def __init__(self,sid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sid=sid


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

<<<<<<< HEAD

class RandomAgent(Agent):
    def __init__(self, _id=None, name="Random", password=None, rate=1600, current_contests=[]):
        super().__init__(_id,name,password, rate, current_contests)

    def act(self, game):
        actions = game.get_all_possible_actions()
        return actions[randrange(0, len(actions))]
    def __str__(self):
        return str(self.id) + self.name +str(self.rate)

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
=======
>>>>>>> training_ploting
