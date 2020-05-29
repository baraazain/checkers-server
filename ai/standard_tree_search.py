from copy import deepcopy
from typing import Dict, Optional

import random
from math import sqrt, log


from model.game import Action, Game
from .config import MAXIMIZER
from .utils import GameState, evaluate, to_label, ActionEncoder


class Node:

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.stats = {'N': 0, 'W': 0, 'Q': 0}
        self.edges: Dict[int, Edge] = {}

    def is_leaf(self) -> bool:
        return len(self.edges) <= 0


class Edge:
    def __init__(self, in_node: Optional[Node], out_node: Optional[Node], action: Action, action_id: int):
        self.in_node = in_node
        self.out_node = out_node
        self.action = action
        self.action_id = action_id


class MCTree:
    def __init__(self, root: Node, action_encoder: ActionEncoder):
        self.root = root
        self.transation_table = {root.game_state: root}
        self.action_encoder = action_encoder

    def traverse(self, node: Node) -> Node:
        current_node = node
        path = []
        while not current_node.is_leaf():
            max_uct = -1e9

            nb = current_node.stats['N']

            simulation_edge = None

            for idx, edge in enumerate(current_node.edges.values()):
                if edge.out_node.stats['N'] == 0:
                    simulation_edge = edge
                    break

                q = edge.out_node.stats['Q']

                uct = q + sqrt(2 * log(nb)/edge.out_node.stats['N'])
                
                if uct > max_uct:
                    max_uct = uct
                    simulation_edge = edge
            
            path.append(current_node)
            current_node = simulation_edge.out_node

        return current_node, path

    @staticmethod
    def backup(leaf: Node, path: list, value: int):
        
        def update(current_node, current_player):
            player_turn = current_node.game_state.get_player_turn()
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            current_node.stats['N'] += 1
            current_node.stats['W'] += value * direction
            current_node.stats['Q'] = current_node.stats['W'] / current_node.stats['N']

        current_player_turn = leaf.game_state.get_player_turn()
        current_node = leaf
        while path:
            update(current_node, current_player_turn)
            current_node = path.pop()
        update(current_node, current_player_turn)

    def expand(self, node: Node):
        possible_actions, possible_states = node.game_state.get_all_possible_states()
        actions_labels = list(map(to_label, possible_actions))
        actions_ids = self.action_encoder.transform(actions_labels)
        for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
            try:
                child = self.transation_table[new_state]
            except KeyError:
                child = Node(new_state)
                self.transation_table[new_state] = child

            node.edges[action_id] = Edge(node, child, action, action_id)
    
    def simulate(self):
        if self.root.is_leaf():
            self.expand(self.root)
        leaf, path = self.traverse(self.root)
        if leaf.stats['N'] == 0:
            value = self.rollout(leaf)
        else:
            self.expand(leaf)

            value = self.rollout(leaf)
        
        self.backup(leaf, path, value)

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
        print(self.root.edges)
        av_tuples = []
        for edge in edges.values():
            prob = edge.out_node.stats['N'] / self.root.stats['N']
            value = edge.out_node.stats['Q']
            action = edge.action
            av_tuples.append((action, value, prob))

        return av_tuples
    
    def update_root(self, action_id):
        if self.root.is_leaf():
            self.expand(self.root)

        self.root = self.root.edges[action_id].out_node
        for edge in self.root.edges:
            edge.in_node = None            
