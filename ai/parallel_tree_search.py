import random
from math import sqrt, log
from typing import Optional

from model.game import Action, Game, MAXIMIZER
from .utils import GameState, evaluate, to_label, ActionEncoder, get_action_space


class Node:

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.edges = {}


class Edge:
    def __init__(self, in_node: Optional[Node], out_node: Optional[Node], action: Action, action_id: int):
        self.in_node = in_node
        self.out_node = out_node
        self.stats = {'W': 0, 'N': 0}
        self.action = action
        self.action_id = action_id


class MCTree:

    def __init__(self, initial_state: GameState):
        self.root = Node(initial_state)
        self.current_root = self.root
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length, initial_state.board_width))
        self.tree = {initial_state: self.root}

    @staticmethod
    def traverse(node):
        current_node = node
        # print('traversing')
        path = []
        while current_node.edges:
            max_uct = -1e9

            nb = 0
            for edge in current_node.edges.values():
                nb += edge.stats['N']

            simulation_edge = None

            for edge in current_node.edges.values():
                if edge.stats['N'] == 0:
                    simulation_edge = edge
                    break

                q = edge.stats['W'] / edge.stats['N']

                uct = q + sqrt(2 * log(nb) / edge.stats['N'])

                if uct > max_uct:
                    max_uct = uct
                    simulation_edge = edge

            simulation_edge.stats['W'] -= 1

            simulation_edge.stats['N'] += 1

            path.append(simulation_edge)

            current_node = simulation_edge.out_node

        return current_node, path

    @staticmethod
    def backup(leaf, path, value):
        # print('backup')
        current_player = leaf.game_state.get_player_turn()

        for edge in path:
            player_turn = edge.in_node.game_state.turn
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            edge.stats['W'] += value * direction + 1

    def expand(self, leaf):
        possible_actions, possible_states = leaf.game_state.get_all_possible_states()
        actions_labels = list(map(to_label, possible_actions))
        actions_ids = self.action_encoder.transform(actions_labels)

        for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
            if new_state in self.tree:
                child = self.tree[new_state]
            else:
                child = Node(new_state)
                self.tree[new_state] = child

            leaf.edges[action_id] = Edge(leaf, child, action, action_id)

    @staticmethod
    def rollout(node):
        # print('evaluating')
        game: Game = node.game_state.get_game()

        while not game.end():
            actions = game.get_all_possible_actions()
            action = random.choice(actions)
            game.apply_action(action)

        value = evaluate(game)

        return value if node.game_state.turn == MAXIMIZER else -value

    def simulate(self):
        if not self.current_root.edges:
            self.expand(self.current_root)

        leaf, path = self.traverse(self.current_root)

        self.expand(leaf)

        value = self.rollout(leaf)

        self.backup(leaf, path, value)

    def get_AV(self):
        edges = self.root.edges
        actions = []
        values = []

        for edge in edges.values():
            actions.append(edge.action)
            values.append(edge.stats['W'] / edge.stats['N'])

        return actions, values

    def update_root(self, action):
        action_id = self.action_encoder.transform([to_label(action)])[0]
        if not self.current_root.edges:
            self.expand(self.current_root)

        self.current_root = self.current_root.edges[action_id].out_node

    def reset(self):
        self.current_root = self.root

    def add_states(self, node: Node):
        self.tree[node.game_state] = node
        for edge in node.edges.values():
            self.add_states(edge.out_node)

    def merge(self, edge, other_edge):
        if not edge.out_node.edges:
            if other_edge.out_node.edges:
                edge.out_node = other_edge.out_node
                edge.stats = other_edge.stats
                self.add_states(edge.out_node)
                return False
            else:
                return False
        else:
            if other_edge.out_node.edges:
                for key in edge.stats:
                    edge.stats[key] += other_edge.stats[key]
                return True
            else:
                return False

    def dfs(self, root: Node, other_root: Node):
        if root.game_state != other_root.game_state:
            raise ValueError('can\'nt merge different game state')
        for key in root.edges.keys():
            if self.merge(root.edges[key], other_root.edges[key]):
                self.dfs(root.edges[key].out_node, other_root.edges[key].out_node)
