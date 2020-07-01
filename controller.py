import argparse

import tensorflow as tf

from ai.training_backyard import train_manger

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
    with tf.device('/device:GPU:0'):
        train_manger(0)


if __name__ == '__main__':
    print(args)
    main()
