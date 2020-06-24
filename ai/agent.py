"""The agent module carry out the implementation of AI players.

"""
from abc import ABC
from copy import deepcopy

import random
import time

import tensorflow.keras as tk
import numpy as np

import ai.modified_tree_search as mts
import ai.standard_tree_search as sts
import model.game as gm
from model.actors import Agent
from .utils import GameState, load_best_model


class DummyAgent(Agent):
    """A dumb player that takes random actions.

    """

    def __init__(self):
        super().__init__(0, "Dummy", None)

    def act(self, game):
        paths = game.get_all_possible_actions()
        return paths[random.randrange(0, len(paths))]

    def on_start(self, game):
        pass

    def on_update(self, action):
        pass

class MonteCarloAgent(Agent):
    """A player that uses monte carlo tree search algorithm to take actions.

    """

    def __init__(self, simulations_limit):
        super().__init__(0, "MonteCarlo", None)
        self.simulations_limit = simulations_limit
        self.mct = None
    
    def on_start(self, game: gm.Game):
        self.mct = sts.MCTree(GameState(game))
    
    def on_update(self, action):
        self.mct.update_root(action)
    
    def act(self, game):

        start_time = time.monotonic()
        while time.monotonic() - start_time < self.simulations_limit:
            self.mct.simulate()
   
        actions, values = self.mct.get_AV()
        
        mx_val = -1e9
        best_action = None
        
        for action, value in zip(actions, values):
            if value > mx_val:
                best_action = action
                mx_val = value

        return best_action


class MiniMaxAgent(Agent, ABC):
    def __init__(self):
        super().__init__(None, "Max", None)


class AlphaZero(Agent):
    """A player that uses reinforcement learning and neural networks to take actions.

    """

    def __init__(self, simulation_limit):
        super().__init__(None, "AlphaZero", None)
        self.simulation_limit = simulation_limit

        self.mct = None

    def train_act(self, tau):

        for _ in range(self.simulation_limit):
            self.mct.simulate()

        pi, values = self.mct.get_AV(tau)

        def choose_action():
            if tau == 0:
                # playing deterministically => always choose the maximum probability
                actions = np.argwhere(pi == np.max(pi))
                action_idx = np.random.choice(actions.ravel())
            else:
                # take an experiment with pi as a probability vector then choose the action which happened
                outcomes = np.random.multinomial(1, pi)
                action_idx = np.where(outcomes == 1)[0][0]

            return action_idx, values[action_idx]

        action_id, value = choose_action()

        state_stack = deepcopy(self.mct.state_stack)
        state_stack.push(self.mct.root.game_state)

        return self.mct[action_id], state_stack, value, pi
    
    def build_mct(self, game_state: GameState, model: tk.models.Model):
        self.mct = mts.MCTree(game_state, model)

    def on_update(self, action):
        self.mct.update_root(action)
    
    def on_start(self, game):
        self.mct = mts.MCTree(GameState(game), load_best_model())
    
    def act(self, game):
        pass
