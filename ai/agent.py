import numpy as np

from model.actors import Agent
from .treesearch import *
from .utils import ActionEncoder, get_action_space


class AlphaZero(Agent):
    def __init__(self, simulation_limit, name="AlphaZero"):
        super().__init__(None, name, None)
        self.simulation_limit = simulation_limit

        self.mcts = None

        self.action_encoder = ActionEncoder()
        action_space = np.array(get_action_space())
        self.action_encoder.fit(action_space)

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
        try:
            action = self.mcts.root.edges[action_id].action
        except KeyError:
            print(action_id)
            print(self.mcts.edges.keys())
            raise RuntimeError

        return action, action_id, self.mcts.root.state_stack, value, pi

    def build_mcts(self, state_stack: StateStack, cpuct: float, model: NeuralNetwork):
        self.mcts = MCTree(Node(state_stack, None, 1), cpuct, model, self.action_encoder)

    def update_root(self, action_id):
        if not self.mcts.root.is_leaf():
            self.mcts.root = self.mcts.root.edges[action_id].child_node
            self.mcts.root.parent_node = None
        else:
            self.mcts.expand_and_evaluate(self.mcts.root, self)
            self.mcts.root = self.mcts.root.edges[action_id].child_node
            self.mcts.root.parent_node = None

    def act(self, game):
        pass
