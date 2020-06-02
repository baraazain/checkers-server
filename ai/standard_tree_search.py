from copy import deepcopy
from typing import Dict, Optional

import random
from math import sqrt, log


from model.game import Action, Game
from .config import MAXIMIZER
from .utils import GameState, evaluate, to_label, ActionEncoder, get_action_space


class Node:

    def __init__(self, parent_node, game_state: GameState):
        self.game_state = game_state
        self.stats = {'N': 0, 'W': 0, 'Q': 0}
        self.parent_node = parent_node
        self.edges: Dict[int, Edge] = {}

    def is_leaf(self) -> bool:
        return len(self.edges) <= 0


class Edge:
    def __init__(self, child_node: Optional[Node], action: Action, action_id: int):
        self.child_node = child_node
        self.action = action
        self.action_id = action_id


class MCTree:
    
    def __init__(self, initial_state: GameState):
        self.root = Node(None, initial_state)
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length, initial_state.board_width))

    def traverse(self, node: Node) -> Node:
        current_node = node
        while current_node.edges:
            max_uct = -1e9

            parent_vists = current_node.stats['N']

            simulation_edge = None

            for idx, edge in enumerate(current_node.edges.values()):
                if edge.child_node.stats['N'] == 0:
                    simulation_edge = edge
                    break

                q = edge.child_node.stats['Q']

                uct = q + sqrt(2 * log(parent_vists)/edge.child_node.stats['N'])
                
                if uct > max_uct:
                    max_uct = uct
                    simulation_edge = edge
            
            current_node = simulation_edge.child_node

        return current_node

    @staticmethod
    def backup(leaf: Node, value: int):

        current_player = leaf.game_state.get_player_turn()
        current_node = leaf

        while current_node is not None:
            player_turn = current_node.game_state.get_player_turn()
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            current_node.stats['N'] += 1
            current_node.stats['W'] += value * direction
            current_node.stats['Q'] = current_node.stats['W'] / current_node.stats['N']
            current_node = current_node.parent_node
        
    def expand(self, node: Node):
        possible_actions, possible_states = node.game_state.get_all_possible_states()
        actions_labels = list(map(to_label, possible_actions))
        actions_ids = self.action_encoder.transform(actions_labels)
        for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
            child = Node(node, new_state)

            node.edges[action_id] = Edge(child, action, action_id)
    
    def simulate(self):
        if not self.root.edges:
            self.expand(self.root)
        leaf = self.traverse(self.root)
        if leaf.stats['N'] == 0:
            value = self.rollout(leaf)
        else:
            self.expand(leaf)

            value = self.rollout(leaf)
        
        self.backup(leaf, value)

    def rollout(self, node: Node) -> float:
        current_node = node
        game: Game = node.game_state.get_game()

        while not game.end():
            actions = game.get_all_possible_actions()
            action = random.choice(actions)
            game.apply_action(action)
        
        value = evaluate(game)
        
        return value if node.game_state.turn == MAXIMIZER else -value

    def get_AV(self):
        edges = self.root.edges
        probs = []
        actions = []
        values = []
        for edge in edges.values():
            prob = edge.child_node.stats['N'] / self.root.stats['N']
            value = edge.child_node.stats['Q']
            action = edge.action
            actions.append(action)
            probs.append(prob)
            values.append(value)
            
        return actions, values, probs
    
    def update_root(self, action):
        action_id = self.action_encoder.transform([to_label(action)])[0]
        if self.root.is_leaf():
            self.expand(self.root)

        self.root = self.root.edges[action_id].child_node
        for edge in self.root.edges.values():
            edge.parent_node = None            
