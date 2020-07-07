from copy import deepcopy
from typing import Dict, Optional, List, Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model

from model.action import Action
from model.game import MAXIMIZER
from .config import EPSILON, ALPHA, CPUCT
from .utils import StateStack, evaluate, to_label, ActionEncoder, GameState, get_action_space


class Node:
    """Monte Carlo tree node
    """
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.edges: Dict[int, Edge] = {}


class Edge:
    """Monte Carlo tree edge as described in the AlphaZero paper.
    """

    def __init__(self, in_node: Node, out_node: Optional[Node], action: Action, action_id: int, flip_flag: bool):
        self.out_node = out_node
        self.in_node = in_node
        self.action = action
        self.action_id = action_id
        self.flip_flag = flip_flag
        self.stats = {'N': 0, 'W': 0., 'Q': 0., 'P': 0.}


class MCTree:
    """Monte Carlo tree search as described in the AlphaZero paper
    """
    def __init__(self, initial_state: GameState, model: Model):
        self.root = Node(initial_state)
        self.model = model
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length))
        self.state_stack = StateStack()
        self.graph = {initial_state: self.root}

    def traverse(self) -> Tuple[Node, StateStack, List[Edge]]:
        """Search in the tree for the best leaf starting from the root of the tree.

        :return: The best leaf node along with game states history and the path list
        """

        current_node = self.root
        state_stack = deepcopy(self.state_stack)
        path = []
        while current_node.edges:
            # Add the current game state to the turns history
            state_stack.push(current_node.game_state)

            max_puct = -1e9

            if current_node is self.root:
                noise = np.random.dirichlet([ALPHA] * len(current_node.edges))
            else:
                noise = []

            # Calculates the children visits sum to get current node visits.
            nb = 0
            for edge in current_node.edges.values():
                nb += edge.stats['N']

            simulation_edge = None

            for idx, edge in enumerate(current_node.edges.values()):
                # If we are in the root node we must add noise to the probability
                if current_node is self.root:
                    probability = ((1 - EPSILON) * edge.stats['P'] + EPSILON * noise[idx])
                else:
                    probability = edge.stats['P']

                u = CPUCT * probability * np.sqrt(nb) / (1 + edge.stats['N'])
                q = edge.stats['Q']

                # maximize puct
                if q + u > max_puct:
                    max_puct = q + u
                    simulation_edge = edge

            path.append(simulation_edge)

            # Traverse down the tree
            current_node = simulation_edge.out_node

        state_stack.push(current_node.game_state)

        return current_node, state_stack, path

    @staticmethod
    def backup(leaf, path, value):
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

            edge.stats['N'] = edge.stats['N'] + 1
            edge.stats['W'] = edge.stats['W'] + value * direction
            edge.stats['Q'] = edge.stats['W'] / edge.stats['N']

    def simulate(self):
        """Do a one time monte carlo tree search simulation

        :return:
        """

        leaf, state_stack, path = self.traverse()

        value = self.expand_and_evaluate(leaf, state_stack)

        self.backup(leaf, path, value)

    def get_predictions(self, state_stack: StateStack):
        """Calculates the value and the probabilities of possible actions of the state stack head

        :param state_stack:
        :return: A tuple of value, probabilities, possible actions keys, possible actions, possible states
        """
        # We retrieve the value of the game state and the logits vector from the neural network
        predictions = self.model(state_stack.get_deep_representation_stack().reshape((1,) +
                                                                                     state_stack.get_input_shape()))

        value = float(predictions[0][0])
        # casting the tensor to a numpy array for the ease of broadcasting
        logits = predictions[1][0].numpy()

        return value, logits

    def expand_and_evaluate(self, leaf: Node, state_stack: StateStack) -> float:
        """
        :param leaf: The leaf node to expand and evaluate
        :param state_stack: The turn history stack
        :return: The evaluation of the leaf
        """

        game_state = leaf.game_state

        leaf_game = game_state.get_game()
        # In case of an End game state we evaluate the leaf directly
        if leaf_game.end():
            evaluation = evaluate(game_state)
            return evaluation if game_state.turn == MAXIMIZER else -evaluation
        else:
            # expanding phase
            paths = leaf_game.get_all_possible_actions()

            for path in paths:
                # for each path we are going to add all of the actions to the tree simultaneously
                current_node = leaf
                current_state = leaf.game_state
                size = len(path)

                for idx, action in enumerate(path):
                    # end of turn flag
                    flip_flag = idx == (size - 1)
                    action_id = self.action_encoder.transform([to_label(action)])[0]
                    game = current_state.get_game()

                    game.apply_action(action)

                    new_state = GameState(game)

                    if flip_flag:
                        new_state.turn = 3 - new_state.turn

                    # check if the child is already in the tree
                    try:
                        child = self.graph[new_state]
                    except KeyError:
                        child = Node(new_state)
                        self.graph[new_state] = child

                    current_state = new_state

                    if action_id not in current_node.edges.keys():
                        current_node.edges[action_id] = Edge(current_node, child, action, action_id, flip_flag)
                        current_node = child
                    else:
                        current_node = current_node.edges[action_id].out_node

            vis = set()

            # evaluate phase
            def dfs(node: Node, current_state_stack):
                if not node.edges:
                    return 0, -1

                vis.add(node.game_state)

                v_sum = 0
                actions_ids = []
                # we aggregate actions ids to get all possible legal actions
                for edge in node.edges.values():
                    actions_ids.append(edge.action_id)

                actions_ids = np.array(actions_ids)

                value, logits = self.get_predictions(current_state_stack)

                # Mask the illegal actions and remove their logits from the vector
                mask = np.ones_like(logits, dtype=bool)
                mask[actions_ids] = False
                # We set the value to -100 making e^Z[illegal neuron] ~ 0
                logits[mask] = -100

                # Applying softmax activation to get the probability vector
                probs = tf.nn.softmax(logits).numpy()

                # add the probability to newly added nodes
                # sum the values of the children
                # remember that W = sum of the rewards for node children
                for edge in node.edges.values():
                    edge.stats['P'] = probs[edge.action_id]

                    # recursively traverse the tree until we get to a leaf
                    left_most_element = None
                    if len(current_state_stack) >= 5:
                        left_most_element = current_state_stack.pop_left()
                    current_state_stack.push(edge.out_node.game_state)

                    if edge.out_node.game_state not in vis:
                        ret_value, inc = dfs(edge.out_node, current_state_stack)
                        v_sum += ret_value

                        # update the edge statistics
                        edge.stats['N'] = 1 + inc
                        edge.stats['W'] = ret_value
                        edge.stats['Q'] = edge.stats['W']

                    current_state_stack.pop()
                    if left_most_element is not None:
                        current_state_stack.push_left(left_most_element)

                return v_sum + value, 0

            return dfs(leaf, state_stack)[0]

    def get_AV(self, tau):
        """Calculates the action value pairs

        :param tau: The temperature value
        :return: the probability vector and values vector
        """

        pi = np.zeros(self.action_encoder.space_shape)
        values = np.zeros(self.action_encoder.space_shape)

        for edge in self.root.edges.values():
            pi[edge.action_id] = edge.stats['N']
            values[edge.action_id] = edge.stats['Q']

        # Search probabilities pi are returned proportional to N^(1/tau)
        pi = tf.math.pow(pi, 1 / max(0.01, tau))  # taking maximum to avoid division by zero and to prevent overflow

        # Normalize the vector to represent a probability vector
        pi = tf.math.divide(pi, tf.math.reduce_sum(pi)).numpy()

        return pi, values

    def update_root(self, action):
        action_id = self.action_encoder.transform([to_label(action)])[0]
        self.state_stack.push(self.root.game_state)

        if not self.root.edges:
            self.expand_and_evaluate(self.root, self.state_stack)

        self.root = self.root.edges[action_id].out_node

    def __getitem__(self, item):
        edge = self.root.edges[item]
        return edge.action, edge.flip_flag
