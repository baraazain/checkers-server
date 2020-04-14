from .game import Player, GameState
from random import randrange


class Human(Player):
    pass


class ConsolePlayer(Human):
    def __init__(self, id, name, password):
        Human.__init__(self, id, name, password)

    def act(self, game: GameState):
        game.print_board()
        actions = game.get_all_possible_actions()
        for idx, action in enumerate(actions):
            print(str(idx + 1) + "." + str(action))
        return actions[int(input('Enter your choice:')) - 1]


class Agent(Player):
    pass


class RandomAgent(Agent):
    def __init__(self):
        Agent.__init__(self, None, "Random", None)

    def act(self, game: GameState):
        actions = game.get_all_possible_actions()
        return actions[randrange(0, len(actions))]


class MiniMaxAgent(Agent):
    def __init__(self, maximum_depth):
        Agent.__init__(self, None, "Max", None)
        self.maximum_depth = maximum_depth

    def max(self, alpha, beta, depth, game: GameState):
        if depth == self.maximum_depth or game.is_terminal() is not None:
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

    def min(self, alpha, beta, depth, game: GameState):
        if depth == self.maximum_depth or game.is_terminal() is not None:
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

    def evaluate(self, game: GameState):
        pass

    def act(self, game: GameState):
        value, action = self.max(int(-1e9), int(1e9), 0, game)
        return action
