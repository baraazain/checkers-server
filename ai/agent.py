from .treeSearch import *
from .utils import ActionEncoder, get_action_space, StateStack, to_label
from model.actors import Agent
from model.game import Action
from copy import deepcopy
import numpy as np

class AlphaZero(Agent):
    def __init__(self, simulation_limit, cpuct, model, pov, name="AlphaZero"):
        Agent.__init__(self, None, name, None)
        self.simulation_limit = simulation_limit
        self.model = model
        self.pov = pov
        self.cpuct = cpuct
        
        self.mcts: MCTree = None
        
        self.action_encoder = ActionEncoder()
        action_space = np.array(get_action_space(10, 10))
        self.action_space_shape = action_space.shape
        self.action_encoder.fit(action_space)

    def get_preds(self, state_stack: StateStack):
        preds = self.model.predict(state_stack.get_deep_representation_stack().
                                   reshape((1,) + state_stack.get_input_shape()))
        value = preds[0][0]
        logits = preds[1][0]

        possible_actions, possible_states = state_stack.head.get_all_possible_states()

        actions_labels = np.array(list(map(to_label, possible_actions)))
        actions_cats = self.action_encoder.label_transform(actions_labels)

        mask = np.ones_like(logits, dtype=bool)
        mask[actions_cats] = False
        logits[mask] = -100

        import tensorflow as tf
        probs = np.array(tf.nn.softmax(logits))

        return value, probs, actions_cats, possible_actions, possible_states
    
    def get_AV(self):
        edges = self.mcts.root.edges
        pi = np.zeros(self.action_space_shape)
        values = np.zeros(self.action_space_shape)

        for edge in edges.values():
            pi[edge.action_id] = edge.get_child().stats['N']
            values[edge.action_id] = edge.get_child().stats['Q']

        pi = pi / self.mcts.root.stats['N']
        return pi, values
    
    def choose_action(self, pi, values, tau):
        if tau == 0:
            actions = np.argwhere(pi == np.max(pi))
            action_idx = np.random.choice(actions.ravel())
        else:
            outcomes = np.random.multinomial(1, pi)
            action_idx = np.where(outcomes == 1)[0][0]
        
        return action_idx, values[action_idx]
    
    def train_act(self, tau):
        for _ in range(self.simulation_limit):
            self.mcts.simulate(self)
        
        pi ,values = self.get_AV()
        
        action_id, value = self.choose_action(pi, values, tau)
        
        return self.mcts.root.edges[action_id].action, action_id, self.mcts.root.get_state(), value, pi
        
    def build_mcts(self, state_stack):
        self.mcts = MCTree(Node(state_stack,None, 1), self.cpuct)
    
    def update_root(self, action_id):
        if not self.mcts.root.is_leaf():
            self.mcts.root = self.mcts.root.edges[action_id].get_child()
            self.mcts.root.p = None
        else:
            self.mcts.expand_and_evaluate(self.mcts.root, self)
            self.mcts.root = self.mcts.root.edges[action_id].get_child()
            self.mcts.root.p = None
            
    def act(self, game):
        pass
