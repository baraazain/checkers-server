import argparse
import asyncio

import tensorflow as tf

import ai.config as config
import ai.utils as ut
from ai.training_backyard import generate_data, evaluate, train, get_models

parser = argparse.ArgumentParser(description='Checkers Server.')
parser.add_argument('--single', action='store_true')
parser.add_argument('--level', '-lvl', metavar='level', type=int,
                    help='define the level of the AI player', default=1)

# run like python controller.py --single -lvl 1
# to play multiple player game run
# python controller.py
args = parser.parse_args()


async def start_train():
    with tf.device('/device:GPU:0'):
        current, best = get_models()
        current.load_weights(ut.weights_folder + 'tmp alphazero' + f" {config.CURRENT_VERSION:0>3}" + '.h5')
        i = 0
        iteration = 1
        while True:
            print("loading dataset....")
            dataset = ut.SampleBuilder.load(config.CURRENT_DATASET + i, ''.join([ut.archive_folder, '/tmp']))
            print("training started....")
            if evaluate(1, current, best):
                break
            else:
                generate_data(4, config.CURRENT_DATASET + i)
                train(current, dataset, iteration)
                ut.save_model(current, 'tmp alphazero', config.CURRENT_VERSION + i + 1)

            i += 4
            iteration += 1


async def start_game():
    from model.international_game import InternationalGame
    from ai.agent import DummyAgent
    from model.actors import ConsolePlayer
    game = InternationalGame(1, ConsolePlayer(1, "", ""), DummyAgent(), None)
    # game = InternationalGame(1, DummyAgent(), MiniMaxAgent(pov=2, timeout=3), None)
    # game = InternationalGame.read()
    # from ai.modified_tree_search import Node, MCTree
    # from ai.utils import GameState, load_best_model
    # m_tree = MCTree(GameState(game), load_best_model())
    # m_tree.expand_and_evaluate(m_tree.root, m_tree.state_stack)
    # game.player1 = ConsolePlayer(1, "", "")
    # game.player2 = ConsolePlayer(2, "", "")
    game.init()
    game.player1.on_start(game)
    game.player2.on_start(game)
    while not game.end():
        print(game.grid)
        path = game.get_current_player().act(game)
        print(''.join(list(map(str, path))))
        game.apply_turn(path)
        game.player1.on_update(path)
        game.player2.on_update(path)
    game.print_the_winner()
    print(game.grid)


async def main():
    print('Hello, World')


if __name__ == '__main__':
    print(args)
    asyncio.run(main())
