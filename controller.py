import datetime as dt
import random
import copy
import sys

import numpy as np
import random

from ai.agent import DummyAgent
from model.international_game import InternationalGame


def main():
    random.seed(101)
    game = InternationalGame.read()
    game.current_turn = 2
    print(game.grid)
    actions = game.get_all_possible_actions()
    for action in actions:
        print(action)

    # while not game.end():
    #     action = game.get_current_player().act(game)
    #     while not game.is_legal_action(action):
    #         action = game.get_current_player().act(game)
    #     game.apply_action(action)
    #     print(game.grid)
    # game.print_the_winner()


if __name__ == '__main__':
    main()
