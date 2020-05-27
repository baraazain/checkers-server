import datetime as dt
import random

from model.actors import RandomAgent
from model.international_game import InternationalGame


def main():
    random.seed(101)
    game = InternationalGame(1, RandomAgent(), RandomAgent(), dt.datetime.now())
    game.init()
    print(game.grid)
    while not game.end():
        action = game.get_current_player().act(game)
        while not game.is_legal_action(action):
            action = game.get_current_player().act(game)
        game.apply_action(action)
        print(game.grid)
    game.print_the_winner()

if __name__ == '__main__':
    main()    