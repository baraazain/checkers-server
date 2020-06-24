import datetime
import argparse

from ai.agent import DummyAgent, MiniMaxAgent, MonteCarloAgent
from model.actors import ConsolePlayer
from model.international_game import InternationalGame

parser = argparse.ArgumentParser(description='Checkers Server.')
parser.add_argument('--single', action='store_true')
parser.add_argument('--level', '-lvl', metavar='level', type=int,
                    help='define the level of the AI player', default=1)

# run like python controller.py --single -lvl 1
# to play multiple player game run
# python controller.py
args = parser.parse_args()


def main():
    print('Hello, World')

    game_dict = {
        'multiple': {
            1: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 ConsolePlayer(_id=2, name='Jack', password='123'),
                                 datetime.datetime.now()),

        },

        'single': {
            1: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 DummyAgent(),
                                 datetime.datetime.now()),

            2: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 MonteCarloAgent(simulations_limit=0.5),
                                 datetime.datetime.now()),

            3: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 MonteCarloAgent(simulations_limit=1),
                                 datetime.datetime.now()),

            4: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 MonteCarloAgent(simulations_limit=1.5),
                                 datetime.datetime.now()),

            5: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 MiniMaxAgent(pov=2, initial_depth=3, timeout=2),
                                 datetime.datetime.now()),

            6: InternationalGame(1,
                                 ConsolePlayer(_id=1, name='Mark', password='123'),
                                 MiniMaxAgent(pov=2, initial_depth=3, timeout=3),
                                 datetime.datetime.now()),
        },
    }

    if not args.single:
        game = game_dict['multiple'][1]
    else:
        game = game_dict['single'][args.level]

    game.init()
    game.player1.on_start(game)
    game.player2.on_start(game)

    print(game.grid)
    while not game.end():
        path = game.get_current_player().act(game)
        game.apply_turn(path)
        game.player1.on_update(path)
        game.player2.on_update(path)
        print(game.grid)
    game.print_the_winner()


if __name__ == '__main__':
    print(args)
    main()
