from copy import deepcopy
from typing import Dict, Optional

import numpy as np

from model.game import Action
from .config import EPSILON, ALPHA, MAXIMIZER, CPUCT
from .utils import StateStack, evaluate, to_label, ActionEncoder, GameState, get_action_space
from .model import NeuralNetwork


class Node:

    def __init__(self, parent_node, game_state: GameState, probability: float):
        self.parent_node: Optional[Node] = parent_node
        self.game_state = game_state
        self.stats = {'N': 0, 'W': 0, 'Q': 0, 'P': probability}
        self.edges: Dict[int, Edge] = {}

    def is_leaf(self) -> bool:
        return len(self.edges) <= 0


class Edge:
    def __init__(self, child_node: Node, action: Action, action_id: int):
        self.child_node = child_node
        self.action = action
        self.action_id = action_id


class MCTree:
    def __init__(self, initial_state: GameState, model: NeuralNetwork):
        self.root = Node(None, initial_state, 1)
        self.CPUCT = CPUCT
        self.model = model
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length, initial_state.board_width))

    def traverse(self) -> Node:
        current_node = self.root
        state_stack = StateStack()

        while current_node.edges:

            state_stack.push(current_node.game_state)

            max_puct = -1e9

            noise = np.random.dirichlet([ALPHA] * len(current_node.edges))

            parent_visits = current_node.stats['N']

            simulation_edge = None

            for idx, edge in enumerate(current_node.edges.values()):
                if current_node is self.root:
                    probability = (EPSILON * edge.child_node.stats['P'] + (1 - EPSILON) * noise[idx])
                else:
                    probability = edge.child_node.stats['P']

                u = self.CPUCT * probability * np.sqrt(parent_visits) / (1 + edge.child_node.stats['N'])
                q = edge.child_node.stats['Q']

                if q + u > max_puct:
                    max_puct = q + u
                    simulation_edge = edge

            current_node = simulation_edge.child_node
        
        state_stack.push(current_node.game_state)
        
        return current_node, state_stack

    @staticmethod
    def backup(leaf: Node, value: int):
        current_player = leaf.game_state.turn
        current_node = leaf
        while current_node is not None:
            player_turn = current_node.game_state.turn
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            current_node.stats['N'] += 1
            current_node.stats['W'] += value * direction
            current_node.stats['Q'] = current_node.stats['W'] / current_node.stats['N']
            current_node = current_node.parent_node

    def simulate(self):
        leaf, state_stack = self.traverse()
        value = self.expand_and_evaluate(leaf, state_stack)
        self.backup(leaf, value)

    def get_predictions(self, state_stack: StateStack):
        preds = self.model.predict(state_stack.get_deep_representation_stack().
                                   reshape((1,) + state_stack.get_input_shape()))
        value = preds[0][0]
        logits = preds[1][0]

        possible_actions, possible_states = state_stack.head.get_all_possible_states()

        actions_labels = np.array(list(map(to_label, possible_actions)))
        actions_cats = self.action_encoder.transform(actions_labels)

        mask = np.ones_like(logits, dtype=bool)
        mask[actions_cats] = False
        logits[mask] = -100

        import tensorflow as tf
        probs = np.array(tf.nn.softmax(logits))

        return value, probs, actions_cats, possible_actions, possible_states

    def expand_and_evaluate(self, leaf: Node, state_stack:StateStack) -> float:
        game_state = leaf.game_state
        if game_state.is_terminal():
            value = evaluate(game_state)
            return value if game_state.turn == MAXIMIZER else -value
        else:
            value, probs, actions_ids, possible_actions, possible_states = self.get_predictions(state_stack)

            for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
                child = Node(leaf, new_state,  probs[action_id])
                edge = Edge(child, action, action_id)
                leaf.edges[action_id] = edge
            return value

    def get_AV(self):
        edges = self.root.edges
        pi = np.zeros(self.action_encoder.space_shape)
        values = np.zeros(self.action_encoder.space_shape)

        for edge in edges.values():
            pi[edge.action_id] = edge.child_node.stats['N']
            values[edge.action_id] = edge.child_node.stats['Q']

        pi = pi / self.root.stats['N']
        return pi, values
    
    def update_root(self, action):
        action_id = self.action_encoder.transform([to_label(action)])[0]
        if not self.root.edges:
            self.expand(self.root)

        self.root = self.root.edges[action_id].child_node
        for edge in self.root.edges.values():
            edge.parent_node = None  
            
    def __getitem__(self, item):
        if item not in self.root.edges.keys():
            raise KeyError(str(item))
        return self.root.edges[item].action
