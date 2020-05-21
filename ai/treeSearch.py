from copy import deepcopy
from typing import Dict, Optional

import numpy as np

from model.game import Action
from .config import EPSILON, ALPHA, MAXIMIZER
from .utils import StateStack, evaluate, to_label, ActionEncoder
from .model import NeuralNetwork


class Node:

    def __init__(self, state_stack: StateStack, parent_node, probability: float):
        self.state_stack = state_stack
        self.parent_node: Optional[Node] = parent_node
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
    def __init__(self, root: Node, CPUCT: float, model: NeuralNetwork, action_encoder: ActionEncoder):
        self.root = root
        self.CPUCT = CPUCT
        self.model = model
        self.action_encoder = action_encoder

    def traverse(self) -> Node:
        current_node = self.root

        while not current_node.is_leaf():
            max_puct = -1e9

            noise = np.random.dirichlet([ALPHA] * len(current_node.edges))

            nb = current_node.stats['N']

            simulation_edge = None

            for idx, edge in enumerate(current_node.edges.values()):
                if current_node is self.root:
                    probability = (EPSILON * edge.child_node.stats['P'] + (1 - EPSILON) * noise[idx])
                else:
                    probability = edge.child_node.stats['P']

                u = self.CPUCT * probability * np.sqrt(nb) / (1 + edge.child_node.stats['N'])
                q = edge.child_node.stats['Q']

                if q + u > max_puct:
                    max_puct = q + u
                    simulation_edge = edge

            current_node = simulation_edge.child_node

        return current_node

    @staticmethod
    def backup(leaf: Node, value: int):
        current_player = leaf.state_stack.head.get_player_turn()
        current_node = leaf
        while current_node is not None:
            player_turn = current_node.state_stack.head.get_player_turn()
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            current_node.stats['N'] += 1
            current_node.stats['W'] += value * direction
            current_node.stats['Q'] = current_node.stats['W'] / current_node.stats['N']
            current_node = current_node.parent_node

    def simulate(self):
        leaf = self.traverse()
        value = self.expand_and_evaluate(leaf)
        self.backup(leaf, value)

    def get_predictions(self, state_stack: StateStack):
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

    def expand_and_evaluate(self, leaf: Node) -> float:
        game_state = leaf.state_stack.head
        if game_state.is_terminal():
            value = evaluate(game_state)
            return value if game_state.turn == MAXIMIZER else -value
        else:
            value, probs, actions_ids, possible_actions, possible_states = self.get_predictions(leaf.state_stack)

            for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
                new_state_stack = deepcopy(leaf.state_stack)
                new_state_stack.push(new_state)
                child = Node(new_state_stack, leaf, probs[action_id])
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
