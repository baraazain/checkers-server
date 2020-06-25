"""A module that carry out the implementation of standard Monte Carlo tree search algorithm.
"""
import random
from math import sqrt, log
from typing import Optional, List, Tuple

from model.game import Game, MAXIMIZER
from model.action import Action
from .utils import GameState, evaluate


class Node:
    """Monte Carlo tree node.
    """

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.edges = []


class Edge:
    """Monte Carlo tree edge.
    """

    def __init__(self, in_node: Node, out_node: Optional[Node], action: List[Action]):
        self.in_node = in_node
        self.out_node = out_node
        self.stats = {'W': 0, 'N': 0}
        self.action = action


class MCTree:
    """Monte Carlo tree.
    """

    def __init__(self, initial_state: GameState):
        self.root = Node(initial_state)
        self.graph = {initial_state: self.root}

    @staticmethod
    def traverse(node: Node) -> Tuple[Node, List[Edge]]:
        """Search in the tree for the best leaf.
        :param node: The starting node
        :return: The best leaf node along with the path list
        """

        current_node = node
        path: List[Edge] = []

        while current_node.edges:
            max_uct = -1e9

            # Calculates the children visits sum to get current node visits.
            nb = 0
            for edge in current_node.edges:
                nb += edge.stats['N']

            simulation_edge = None

            for edge in current_node.edges:
                if edge.stats['N'] == 0:
                    # If we have never visited this child then the uct is going to be infinite.
                    simulation_edge = edge
                    break

                # Calculates the average of the rewards.
                q = edge.stats['W'] / edge.stats['N']

                # Calculates the upper confidence bound defined by the equation.
                uct = q + sqrt(2 * log(nb) / edge.stats['N'])

                # Maximize uct.
                if uct > max_uct:
                    max_uct = uct
                    simulation_edge = edge

            path.append(simulation_edge)

            # Traverse down the tree.
            current_node = simulation_edge.out_node

        return current_node, path

    @staticmethod
    def backup(leaf: Node, path: List[Edge], value: int):
        """Backpropagates the value of endgame to the root node.

        :param leaf: The starting leaf node
        :param path: The path back to root
        :param value: The value of the leaf node
        :return:
        """

        current_player = leaf.game_state.get_player_turn()

        for edge in path:
            player_turn = edge.in_node.game_state.turn
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            edge.stats['N'] += 1

            edge.stats['W'] += value * direction

    def expand(self, leaf: Node):
        """Adds the node children to the search tree.

        :param leaf: The leaf node to expand
        :return:
        """
        possible_actions, possible_states = leaf.game_state.get_all_possible_states()

        for path, new_state in zip(possible_actions, possible_states):
            # Check if the new state is already in the graph dictionary
            try:
                child = self.graph[new_state]
            except KeyError:
                child = Node(new_state)
                self.graph[new_state] = child

            leaf.edges.append(Edge(leaf, child, path))

    @staticmethod
    def rollout(node: Node):
        """Play a randomized game and evaluates the resulting end game.

        :param node: The node which carry out the starting state
        :return: End game evaluation
        """

        game: Game = node.game_state.get_game()

        while not game.end():
            paths = game.get_all_possible_actions()
            path = random.choice(paths)
            game.apply_turn(path)

        value = evaluate(game)

        # We need to set the correct value of the evaluation as evaluate function
        # calculates it from maximizer point of view
        return value if node.game_state.turn == MAXIMIZER else -value

    def simulate(self):
        """Do a one time monte carlo tree search simulation

        :return:
        """
        if not self.root.edges:
            self.expand(self.root)

        leaf, path = self.traverse(self.root)

        self.expand(leaf)

        value = self.rollout(leaf)

        self.backup(leaf, path, value)

    def get_AV(self) -> Tuple[List[Action], List[float]]:
        """Calculates the action value pairs.

        :return: A tuple of actions and their respective visits
        """

        edges = self.root.edges
        actions = []
        values = []

        for edge in edges:
            actions.append(edge.action)
            values.append(edge.stats['N'])

        return actions, values

    def update_root(self, path: List[Action]):
        if not self.root.edges:
            self.expand(self.root)

        t = ''.join(list(map(str, path)))

        for edge in self.root.edges:
            s = ''.join(list(map(str, edge.action)))

            if s == t:
                self.root = edge.out_node
                break
