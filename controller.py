# import multiprocessing as mp
import time

# import ai.parallel_tree_search as pts
# import ai.utils as uty
from model.international_game import InternationalGame
import random
import copy
import sys

import pickle

import numpy as np
import random

from ai.agent import DummyAgent, MiniMaxAgent, MonteCarloAgent
from model.international_game import InternationalGame


# def simulate(mct):
#     for _ in range(200):
#         mct.simulate()
#     return mct

def main():
    print('Hello, World')
    # s = ''
    # print(s.join(['fuck', ' ababa']))
    # tree_error = None
    # reject_error = None
    # with tf.device('/device:GPU:0'):
    #     start_time = time.monotonic()
    #     try:
    #         train_manger(1)
    #     except RejectedActionError as reject_e:
    #         print('rejected')
    #         reject_error = reject_e
    #     except TreeError as tree_e:
    #         print('search error')
    #         tree_error = tree_e
    #     print(f'slept for {time.monotonic() - start_time}')

    # game = InternationalGame(1, MiniMaxAgent(pov=1, initial_depth=3, timeout=2),
    #                          MiniMaxAgent(pov=2, initial_depth=3, timeout=2), None)

    game = InternationalGame(1, MonteCarloAgent(simulations_limit=0.5),
                             MiniMaxAgent(pov=2, initial_depth=3, timeout=2), None)

    game.init()
    game.player1.on_start(game)
    game.player2.on_start(game)

    # game = InternationalGame.read()
    # game.player1 = DummyAgent()
    # game.player2 = DummyAgent()
    # game.current_turn = 2

    print(game.grid)
    while not game.end():
        path = game.get_current_player().act(game)
        game.apply_turn(path)
        game.player1.on_update(path)
        game.player2.on_update(path)
        print(game.grid)
    game.print_the_winner()

    # game = InternationalGame(1, None, None, None)
    # game.init()

    # mct = pts.ParallelMCTree(uty.GameState(game))
    # mct1 = pts.ParallelMCTree(uty.GameState(game))
    # mct2 = pts.ParallelMCTree(uty.GameState(game))
    # mct3 = pts.ParallelMCTree(uty.GameState(game))
    #
    # start_t = time.monotonic()
    #
    # with mp.Pool() as p:
    #     mct, mct1, mct2, mct3 = p.map(simulate, [mct, mct1, mct2, mct3])
    # mct.dfs(mct.root, mct1.root)
    # mct.dfs(mct.root, mct2.root)
    # mct.dfs(mct.root, mct3.root)
    #
    # print(time.monotonic() - start_t)
    #
    # mct4 = pts.ParallelMCTree(uty.GameState(game))
    #
    # start_t = time.monotonic()
    #
    # for _ in range(200):
    #     #start_t1 = time.monotonic()
    #     mct4.simulate()
    #     #print(time.monotonic() - start_t1)
    #
    # print(time.monotonic() - start_t)
    #
    # print(len(mct.tree))


if __name__ == '__main__':
    main()
