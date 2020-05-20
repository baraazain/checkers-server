from model.internationalGame import InternationalGame
from model.actors import RandomAgent, ConsolePlayer
import datetime as dt
import random


def main():
    random.seed(101)
    game = InternationalGame(1, RandomAgent(), RandomAgent(), dt.datetime.now())
    game.init()
    print(game.grid)
    while not game.end():
        action = game.getCurrentPlayer().act(game)
        while not game.isLegalAction(action):
            action = game.getCurrentPlayer().act(game)
        game.applyAction(action)
        print(game.grid)
    game.printTheWinner()


if __name__ == '__main__':
    main()
