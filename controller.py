from model.InternationalGame import InternationalGame
from model.Actors import RandomAgent
import datetime as dt


def main():
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
