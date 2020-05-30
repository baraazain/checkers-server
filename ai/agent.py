from abc import ABC, abstractmethod

import numpy as np

from model.actors import Agent
from .utils import ActionEncoder, get_action_space, GameState, to_label, load_best_model
from .model import NeuralNetwork

import ai.standard_tree_search as sts
import ai.modified_tree_search as mts
import model.game as gm


class DummyAgent(Agent):
    def __init__(self):
        super().__init__(0, "Dummy", None)

    def act(self, game):
        actions = game.get_all_possible_actions()
        return actions[randrange(0, len(actions))]

    def on_start(self, game):
        pass

    def on_update(self, action):
        pass


class MonteCarloAgent(Agent):
    def __init__(self, simulations_limit):
        super().__init__(0, "Monte Carlo", None)
        self.simulations_limit = simulations_limit
        self.mct = None
    
    def on_start(self, game: gm.Game):
        self.mct = sts.MCTree(GameState(game))
    
    def on_update(self, action):
        self.mct.update_root(action)
    
    def act(self, game):

        for _ in range(self.simulations_limit):
            self.mct.simulate()
   
        actions, values, _ = self.mct.get_AV()
        
        mx_val = -1e9
        best_action = None
        
        for action, value in zip(actions, values):
            if value > mx_val:
                best_action = action
                mx_val = value

        return best_action


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


class AlphaZero(Agent):
    def __init__(self, simulation_limit):
        super().__init__(None, "AlphaZero", None)
        self.simulation_limit = simulation_limit

        self.mct = None

    def train_act(self, tau):
        
        def choose_action(pi, values, tau):
            if tau == 0:
                actions = np.argwhere(pi == np.max(pi))
                action_idx = np.random.choice(actions.ravel())
            else:
                outcomes = np.random.multinomial(1, pi)
                action_idx = np.where(outcomes == 1)[0][0]

            return action_idx, values[action_idx]
        
        for _ in range(self.simulation_limit):
            self.mct.simulate()

        pi, values = self.mct.get_AV()

        action_id, value = choose_action(pi, values, tau)

        return self.mct[action_id], self.mct.root.state_stack, value, pi
    
    def build_mct(self, game_state: GameState, model: NeuralNetwork):
        self.mct = mts.MCTree(game_state, model)

    def on_update(self, action):
        self.mct.update_root(action)
    
    def on_start(self, game):
        self.mct = mts.MCTree(GameState(game), load_best_model())
    
    def act(self, game):
        pass
