import time
from typing import Optional, List, Dict

from model.game import Action, MAXIMIZER
from .utils import GameState


class Node:
    """Search tree node.
    """
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.edges: List[Edge] = []


class Edge:
    """Search tree edge.
    """
    def __init__(self, in_node: Node, out_node: Optional[Node], action: Action):
        self.out_node = out_node
        self.in_node = in_node
        self.action = action


class TableItem:
    """Hash table item.
    """
    def __init__(self, node, evaluation=None, best_action=None):
        self.node = node
        self.evaluation = evaluation
        self.best_action = best_action


class AlphaBetaSearch:
    def __init__(self, initial_state: GameState, pov=MAXIMIZER, initial_depth=5, timeout=8):
        self.root = Node(initial_state)
        self.initial_depth = initial_depth
        self.timeout = timeout
        self.start_time = None
        self.timeout_flag = False
        self.transposition_table: Dict[GameState, TableItem] = {}
        self.tree: Dict[GameState, Node] = {}
        self.pov = pov

    @staticmethod
    def evaluate(node: Node) -> int:
        """Calculates the value of the game state at node from the maximizer player point of view.

        :param node: the node to evaluate
        :return: the value of the board
        """
        return 0

    def _cmp_edges(self, edge: Edge) -> int:
        """Defines the comparing method for sorting edges.

        :param edge:
        :return:
        """
        evaluation = self.transposition_table[edge.in_node.game_state].evaluation
        if evaluation is not None:
            return evaluation
        return int(-1e9) if edge.in_node.game_state.turn == 1 else int(1e9)

    def expand(self, node: Node):
        """Adds the node children to the search tree.

        :param node: The node to expand
        :return:
        """
        actions, states = node.game_state.get_all_possible_states()

        for action, state in zip(actions, states):
            try:
                child = self.tree[state]
            except KeyError:
                child = Node(state)
                self.tree[state] = child

            node.edges.append(Edge(node, child, action))

    def memo(self, node, evaluation, best_action):
        """Save the node in the hashtable

        :param node: The node to save
        :param evaluation: The value of the board at node
        :param best_action: The best action to take at node
        :return:
        """
        table_item = self.transposition_table[node.game_state]
        table_item.evaluation = evaluation
        table_item.best_action = best_action

    def min(self, node: Node, depth: int, start_time: float, alpha: int = -1e9, beta: int = 1e9):
        if depth == 0 or node.game_state.is_terminal():
            evaluation = -self.evaluate(node)
            self.transposition_table[node.game_state] = TableItem(node, evaluation)
            return evaluation, None

        if time.monotonic() - start_time >= self.timeout:
            self.timeout_flag = True
            return None, None

        try:
            table_item = self.transposition_table[node.game_state]

            if table_item.evaluation is not None:
                return table_item.evaluation, table_item.best_action
        except KeyError:
            self.transposition_table[node.game_state] = TableItem(node)

        if not node.edges:
            self.expand(node)

        best_action = node.edges[0].action

        for edge in node.edges:
            if edge.out_node.game_state.turn == 1:
                evaluation, _ = self.max(edge.out_node, depth - 1, start_time, alpha, beta)

                if self.timeout_flag:
                    node.edges.sort(key=self._cmp_edges)
                    return None, None

                if evaluation < beta:
                    beta = evaluation
                    best_action = edge.action

                if alpha >= beta:
                    self.memo(node, alpha, None)
                    node.edges.sort(key=self._cmp_edges)
                    return alpha, None
            else:
                evaluation, _ = self.min(edge.out_node, depth, start_time, alpha, beta)

                if self.timeout_flag:
                    return None, None

                self.memo(node, evaluation, edge.action)
                return evaluation, edge.action

        self.memo(node, beta, best_action)
        node.edges.sort(key=self._cmp_edges)
        return beta, best_action

    def max(self, node: Node, depth: int, start_time: float, alpha: int = -1e9, beta: int = 1e9):
        if depth == 0 or node.game_state.is_terminal():
            evaluation = self.evaluate(node)
            self.transposition_table[node.game_state] = TableItem(node, evaluation)
            return evaluation, None

        if time.monotonic() - start_time >= self.timeout:
            self.timeout_flag = True
            return None, None

        try:
            table_item = self.transposition_table[node.game_state]

            if table_item.evaluation is not None:
                return table_item.evaluation, table_item.best_action
        except KeyError:
            self.transposition_table[node.game_state] = TableItem(node)

        if not node.edges:
            self.expand(node)

        best_action = node.edges[0].action

        for edge in node.edges:
            if edge.out_node.game_state.turn == 2:
                evaluation, _ = self.min(edge.out_node, depth - 1, start_time, alpha, beta)

                if self.timeout_flag:
                    node.edges.sort(key=self._cmp_edges, reverse=True)
                    return None, None

                if evaluation > alpha:
                    alpha = evaluation
                    best_action = edge.action

                if alpha >= beta:
                    self.memo(node, beta, None)
                    node.edges.sort(key=self._cmp_edges, reverse=True)
                    return beta, None
            else:
                evaluation, _ = self.max(edge.out_node, depth, start_time, alpha, beta)

                if self.timeout_flag:
                    return None, None

                self.memo(node, evaluation, edge.action)
                return evaluation, edge.action

        self.memo(node, alpha, best_action)
        node.edges.sort(key=self._cmp_edges, reverse=True)
        return alpha, best_action

    def get_best_action(self):
        i = 0
        ret_action = None
        self.timeout_flag = False
        start_time = time.monotonic()

        while True:
            self.transposition_table.clear()
            if self.pov == MAXIMIZER:
                _, action = self.max(self.root, self.initial_depth + i, start_time)
            else:
                _, action = self.min(self.root, self.initial_depth + i, start_time)

            if self.timeout_flag:
                break

            ret_action = action
            i += 1

        return ret_action

    def update_root(self, action):
        pass
