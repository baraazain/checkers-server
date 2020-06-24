from .utils import GameState
from .standard_tree_search import Node, MCTree


# TODO: refactor the module and use a procedural approach rather than inheritance

class ParallelMCTree(MCTree):

    def __init__(self, initial_state: GameState):
        super().__init__(initial_state)

    def add_states(self, node: Node):
        self.graph[node.game_state] = node
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
