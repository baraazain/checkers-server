import argparse

import tensorflow as tf

import ai.utils as ut
from ai.agent import MiniMaxAgent
from model.action import Action
from model.utils import to_json

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
    # from ai.training_backyard import generate_data
    # with tf.device('/device:GPU:0'):
    #     generate_data()

    # from ai.utils import load_best_model, get_action_space
    # print(get_action_space())
    # load_best_model()
    # # print(load(f))
    from model.international_game import InternationalGame
    from ai.agent import DummyAgent, MonteCarloAgent, MiniMaxAgent, AlphaZero
    from model.actors import ConsolePlayer
    game = InternationalGame(1, ConsolePlayer(2, "", ""), MiniMaxAgent(2, timeout=2, initial_depth=3), None)
    # game = InternationalGame(1, DummyAgent(), MiniMaxAgent(pov=2, timeout=3), None)
    # game = InternationalGame.read()
    # from ai.modified_tree_search import Node, MCTree
    # from ai.utils import GameState, load_best_model
    # m_tree = MCTree(GameState(game), load_best_model())
    # m_tree.expand_and_evaluate(m_tree.root, m_tree.state_stack)
    # game.player1 = ConsolePlayer(1, "", "")
    # game.player2 = ConsolePlayer(2, "", "")
    game.init()
    # print(game.grid[0][1].piece)
    # print(game.grid[1][2].piece)
    # ans, piece = game.correct_capture(Action(game.grid[0][1], game.grid[2][3], game.player1))
    # print(ans)

    game.player1.on_start(game)
    game.player2.on_start(game)
    while not game.end():
        print(game.grid)
        path = game.get_current_player().act(game)
        print(''.join(list(map(str, path))))
        game.apply_turn(path)
        game.player1.on_update(path)
        game.player2.on_update(path)
    # game.print_the_winner()
    print(game.grid)


if __name__ == '__main__':
    print(args)
    main()
