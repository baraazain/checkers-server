from copy import deepcopy
from typing import Dict, Optional
from math import sqrt, log

import random
import multiprocessing as mp

from model.game import Action, Game
from .config import MAXIMIZER
from .utils import GameState, evaluate, to_label, ActionEncoder, get_action_space


class Node:

    def __init__(self, game_state: GameState, lock, edgs):
        self.game_state = game_state
        self.lock = lock
        self.edges = edgs

    def is_leaf(self) -> bool:
        return len(self.edges) <= 0


class Edge:
    def __init__(self, in_node: Optional[Node], out_node: Optional[Node], action: Action, action_id: int, stats):
        self.in_node = in_node
        self.out_node = out_node
        self.stats = stats
        self.action = action
        self.action_id = action_id


class MCTree:
    
    def __init__(self, initial_state: GameState):
        self.manager = mp.Manager()
        self.root = Node(initial_state, self.manager.Lock(), self.manager.dict())
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length, initial_state.board_width))
        self.traverse_queue = mp.JoinableQueue()
        self.rollout_queue = mp.JoinableQueue()
        self.backup_queue = mp.JoinableQueue()
        self.expand_queue = mp.Queue()
        self.consumers = []

        self.consumers.append(mp.Process(target=self.traverse, args=(self.traverse_queue, self.expand_queue), daemon=True))
        self.consumers.append(mp.Process(target=self.rollout, args=(self.rollout_queue,self.backup_queue), daemon=True))
        self.consumers.append(mp.Process(target=self.rollout, args=(self.rollout_queue,self.backup_queue), daemon=True))
        self.consumers.append(mp.Process(target=self.backup, args=(self.backup_queue,), daemon=True))

        for p in self.consumers:
            p.start()

    @staticmethod
    def traverse(in_queue, out_queue):
        while True:
            current_node = in_queue.get()
            # print('traversing')
            path = []
            while current_node.edges:
                # print('waiting for node lock')
                current_node.lock.acquire()
                # print('acquired node lock')
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

                    uct = q + sqrt(2 * log(nb)/edge.stats['N'])
                
                    if uct > max_uct:
                        max_uct = uct
                        simulation_edge = edge
            
                simulation_edge.stats['W'] -= 1
                
                path.append(simulation_edge)

                current_node.lock.release()
           
                current_node = simulation_edge.out_node

            out_queue.put((current_node, path))

            in_queue.task_done()

    @staticmethod
    def backup(in_queue):
        while True:
            # print('waiting for leaf node')
            leaf, path, value = in_queue.get()
            # print('backup')
            current_player = leaf.game_state.get_player_turn()
            current_node = leaf

            for edge in path:
                player_turn = edge.in_node.game_state.turn
                if player_turn == current_player:
                    direction = 1
                else:
                    direction = -1
                # print('waiting for edge lock')
                with edge.in_node.lock:
                    # print('acquired edge lock')
                    edge.stats['N'] += 1

                    edge.stats['W'] += value * direction + 1

            in_queue.task_done()
   
    @staticmethod    
    def expand(node, manager, action_encoder):
        possible_actions, possible_states = node.game_state.get_all_possible_states()
        actions_labels = list(map(to_label, possible_actions))
        actions_ids = action_encoder.transform(actions_labels)
        for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
            child = Node(new_state, manager.Lock(), manager.dict())

            node.edges[action_id] = Edge(node, child, action, action_id, manager.dict({'N': 0, 'W': 0}))
            
    @staticmethod
    def rollout(in_queue, out_queue):
        while True:
            node, path = in_queue.get()
            # print('evaluating')
            game: Game = node.game_state.get_game()

            while not game.end():
                actions = game.get_all_possible_actions()
                action = random.choice(actions)
                game.apply_action(action)
        
            value = evaluate(game)
        
            out_queue.put((node, path, value if node.game_state.turn == MAXIMIZER else -value))
            
            in_queue.task_done()
                
    def simulate(self, sims=32):
        # print(f'adding the root {sims} time')
        for i in range(sims):
            self.traverse_queue.put_nowait(self.root)

        for i in range(sims):
            # print('waiting for leafs')
            leaf, path = self.expand_queue.get()
            self.rollout_queue.put((leaf, path))
            # print('expanding')
            self.expand(leaf, self.manager, self.action_encoder)
        
        self.rollout_queue.join()
        self.backup_queue.join()
        # print(f'end {sims} sims')
    
        
    def __del__(self):
        for p in self.consumers:
            p.kill()
        del self.root
        del self.manager
        del self.action_encoder
        del self.traverse_queue
        del self.rollout_queue
        del self.backup_queue
        del self.expand_queue
        del self.consumers

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

