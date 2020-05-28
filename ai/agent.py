import numpy as np

from model.actors import Agent
from .treesearch import *
from .utils import ActionEncoder, get_action_space, GameState

# from .config import CPUCT


class AlphaZero(Agent):
    def __init__(self, simulation_limit, name="AlphaZero"):
        super().__init__(None, name, None)
        self.simulation_limit = simulation_limit

        self.mcts = None

        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space())

    @staticmethod
    def choose_action(pi, values, tau):
        if tau == 0:
            actions = np.argwhere(pi == np.max(pi))
            action_idx = np.random.choice(actions.ravel())
        else:
            outcomes = np.random.multinomial(1, pi)
            action_idx = np.where(outcomes == 1)[0][0]

        return action_idx, values[action_idx]

    def train_act(self, tau):
        for _ in range(self.simulation_limit):
            self.mcts.simulate()

        pi, values = self.mcts.get_AV()

        action_id, value = self.choose_action(pi, values, tau)

        return self.mcts[action_id], self.mcts.root.state_stack, value, pi

    def build_mcts(self, state_stack: StateStack, cpuct: float, model: NeuralNetwork):
        self.mcts = MCTree(Node(state_stack, None, 1), cpuct, model, self.action_encoder)
    
    def on_update(self, action):
        action_id = self.action_encoder.transform([action])
        self.mcts.update_root(action_id)
    
    def on_start(self, game):
        # self.build_mcts(StateStack(deepcopy(GameState(game))), config.CPUCT, load_best_model())
        pass
    
    def act(self, game):
        pass