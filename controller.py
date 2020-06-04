import datetime as dt
import random
import copy
import sys
import pickle

import numpy as np
import random

from ai.agent import DummyAgent
from model.international_game import InternationalGame


def main():
    # random.seed(101)
    # game = InternationalGame.read()
    # game.current_turn = 2
    # print(game.grid)
    # actions = game.get_all_possible_actions()
    # for action in actions:
    #     print(action)

    # in this game the bug is within get_all_possible_states
    # particularly in the second action
    # the captured piece will not be removed from the grid
    # note: this game has no move history
    game = pickle.load(open('firstbug_game.pk', 'rb'))
    actions, states = game.get_all_possible_states()
    for action, state in zip(actions, states):
        print(action)
        print(state.grid)
        print('--------------------------------')

    # in this game the bug in within the logic of the maximum capture
    # when we get a piece maximum capture we will force the player
    # to play it only at the start of the capturing path
    # in the next time if the player has another capture
    # he can choose it rather than following the maximum capture path!!
    # checkout the last four moves for better understanding
    # note: this game has all playing history
    game = pickle.load(open('secondbug_game.pk', 'rb'))

    # while not game.end():
    #     action = game.get_current_player().act(game)
    #     while not game.is_legal_action(action):
    #         action = game.get_current_player().act(game)
    #     game.apply_action(action)
    #     print(game.grid)
    # game.print_the_winner()


if __name__ == '__main__':
    main()
