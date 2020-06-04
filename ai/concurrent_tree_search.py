from copy import deepcopy
from typing import Dict, Optional
from math import sqrt, log

import random
import asyncio

from model.game import Action, Game, MAXIMIZER
from .utils import GameState, evaluate, to_label, ActionEncoder, get_action_space


class Node:

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.lock = asyncio.Lock()
        self.edges: Dict[int, Edge] = {}

    def is_leaf(self) -> bool:
        return len(self.edges) <= 0


class Edge:
    def __init__(self, in_node: Optional[Node], out_node: Optional[Node], action: Action, action_id: int):
        self.in_node = in_node
        self.out_node = out_node
        self.stats = {'N': 0, 'W': 0}
        self.action = action
        self.action_id = action_id


class MCTree:
    
    def __init__(self, initial_state: GameState):
        self.root = Node(initial_state)
        self.action_encoder = ActionEncoder()
        self.action_encoder.fit(get_action_space(initial_state.board_length, initial_state.board_width))
        self.traverse_queue = asyncio.Queue()
        self.expand_queue = asyncio.Queue()
        self.rollout_queue = asyncio.Queue()
        self.backup_queue = asyncio.Queue()
        self.tasks = []
        for i in range(4):
            self.tasks.append(asyncio.create_task(self.traverse(self.traverse_queue, self.expand_queue)))
            self.tasks.append(asyncio.create_task(self.expand(self.expand_queue, self.rollout_queue, self.action_encoder)))
            self.tasks.append(asyncio.create_task(self.rollout(self.rollout_queue, self.backup_queue)))
            self.tasks.append(asyncio.create_task(self.rollout(self.rollout_queue, self.backup_queue)))
            self.tasks.append(asyncio.create_task(self.backup(self.backup_queue)))


    @staticmethod
    async def traverse(in_queue: asyncio.Queue, out_queue: asyncio.Queue):
        while True:
            current_node = await in_queue.get()
            path = []
            while current_node.edges:
                await current_node.lock.acquire()
                
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

            await out_queue.put((current_node, path))

            in_queue.task_done()

    @staticmethod
    async def backup(in_queue: asyncio.Queue):
        while True:
            leaf, path, value = await in_queue.get()
            current_player = leaf.game_state.get_player_turn()
            current_node = leaf

            for edge in path:
                player_turn = edge.in_node.game_state.turn
                if player_turn == current_player:
                    direction = 1
                else:
                    direction = -1
                async with edge.in_node.lock:
                    edge.stats['N'] += 1

                    edge.stats['W'] += value * direction + 1

            in_queue.task_done()
   
    @staticmethod    
    async def expand(in_queue:asyncio.Queue, out_queue: asyncio.Queue, action_encoder: ActionEncoder):
        while True:
            node, path = await in_queue.get()
            possible_actions, possible_states = node.game_state.get_all_possible_states()
            actions_labels = list(map(to_label, possible_actions))
            actions_ids = action_encoder.transform(actions_labels)
            for action, action_id, new_state in zip(possible_actions, actions_ids, possible_states):
                child = Node(new_state)

                node.edges[action_id] = Edge(node, child, action, action_id)
            
            await out_queue.put((node, path))
            
            in_queue.task_done()

    @staticmethod
    async def rollout(in_queue: asyncio.Queue, out_queue: asyncio.Queue):
        while True:
            node, path = await in_queue.get()
            game: Game = node.game_state.get_game()

            while not game.end():
                actions = game.get_all_possible_actions()
                action = random.choice(actions)
                game.apply_action(action)
        
            value = evaluate(game)
        
            await out_queue.put((node, path, value if node.game_state.turn == MAXIMIZER else -value))
            
            in_queue.task_done()
                
    async def simulate(self, sims=8):

        for i in range(sims):
            self.traverse_queue.put_nowait(self.root)


        await self.traverse_queue.join()
        await self.expand_queue.join()
        await self.rollout_queue.join()
        await self.backup_queue.join()

        # for task in tasks:
            # task.cancel()

        # await asyncio.gather(*tasks, return_exceptions=True)


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

