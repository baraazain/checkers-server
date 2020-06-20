import multiprocessing as mp
import time

import ai.parallel_tree_search as pts
import ai.utils as uty
from model.international_game import InternationalGame
import random
import copy
import sys

import pickle

import numpy as np
import random

from ai.agent import DummyAgent
from model.international_game import InternationalGame


# def simulate(mct):
#     for _ in range(200):
#         mct.simulate()
#     return mct


def main():
    print('Hello, World')
    # game = InternationalGame(1, DummyAgent(), DummyAgent(), None)
    # game.init()
    # from ai.alpha_beta_search import AlphaBetaSearch
    # from ai.utils import GameState
    # search = AlphaBetaSearch(GameState(game))
    # search.get_best_action()
    #
    # print(len(search.tree))
    #
    # print(len(search.transposition_table))

    # while not game.end():
    #     action = game.get_current_player().act(game)
    #     while not game.is_legal_action(action):
    #         action = game.get_current_player().act(game)
    #     game.apply_action(action)
    #     print(game.grid)
    # game.print_the_winner()
    #
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
