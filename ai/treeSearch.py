from copy import deepcopy

import numpy as np

from model.game import Action
from .config import EPSILON, ALPHA, MAXIMIZER
from .utils import StateStack, evaluate


class Node:

    def __init__(self, state_stack: StateStack, parent_node, probability):
        self.state_stack = state_stack
        self.parent_node = parent_node
        self.stats = {'N': 0, 'W': 0, 'Q': 0, 'P': probability}
        self.edges = {}

    def is_leaf(self):
        return len(self.edges) <= 0


class Edge:
    def __init__(self, child_node: Node, action: Action, action_id):
        self.child_node = child_node
        self.action = action
        self.action_id = action_id


class MCTree:
    def __init__(self, root, CPUCT):
        self.root = root
        self.CPUCT = CPUCT

    def traverse(self):
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

            current_node = simulation_edge.child

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

    def simulate(self, player):
        leaf = self.traverse()
        value = self.expand_and_evaluate(leaf, player)
        self.backup(leaf, value)

    def expand_and_evaluate(self, leaf: Node, player):
        if leaf.state_stack.head.is_terminal():
            value = evaluate(leaf.state_stack.head)
            return value if player.pov == MAXIMIZER else -value
        else:
            value, probs, actions_cats, possible_actions, possible_states = player.get_preds(leaf.state_stack)

            for action, action_id, new_state in zip(possible_actions, actions_cats, possible_states):
                new_state_stack = deepcopy(leaf.state_stack)
                new_state_stack.push(new_state)
                child = Node(new_state_stack, leaf, probs[action_id])
                edge = Edge(child, action, action_id)
                leaf.edges[action_id] = edge
            return value
