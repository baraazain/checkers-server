import datetime as dt
import random
import copy
import sys


import numpy as np
import random

from model.actors import RandomAgent
from model.international_game import InternationalGame

from ai import standard_tree_search
from ai.utils import GameState

def main():
    random.seed(101)
    game = InternationalGame(1, RandomAgent(), RandomAgent(), dt.datetime.now())
    game.init()
    
    root = standard_tree_search.StandardNode(GameState(game))
    mct = standard_tree_search.MCTree(root)
    for i in range(1000):
        mct.simulate()
    return
    while not game.end():
        action = game.get_current_player().act(game)
        while not game.is_legal_action(action):
            action = game.get_current_player().act(game)
        game.apply_action(action)
        print(game.grid)
    game.print_the_winner()

if __name__ == '__main__':
    main()
    
