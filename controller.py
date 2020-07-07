import argparse

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

    # with tf.device('/device:GPU:0'):
    #     generate_data()

    # print(load(f))
    from model.international_game import InternationalGame
    from ai.agent import DummyAgent
    game = InternationalGame(1, DummyAgent(), DummyAgent(), None)
    game.init()
    game.player1.on_start(game)
    game.player2.on_start(game)
    while not game.end():
        print(game.grid)
        path = game.get_current_player().act(game)
        game.apply_turn(path)
        game.player1.on_update(path)
        game.player2.on_update(path)
    game.print_the_winner()


if __name__ == '__main__':
    print(args)
    main()
