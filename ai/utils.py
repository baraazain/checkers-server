"""A module that carry out the utility's used by the AI algorithms
"""
import pickle
from collections import deque

import numpy as np
import tensorflow.keras as tk
from sklearn.preprocessing import LabelEncoder

import ai.config as config
from model.game import Action, Game
from model.piece import Color, Type
from .model import softmax_cross_entropy_with_logits, build_alphazero_model

archive_folder = 'data/alphazero/datasets/'
weights_folder = 'data/alphazero/weights/'


def to_label(action: Action):
    """Converts the action python object to a label string.

    :param action:
    :return:
    """

    dir_r = action.dst.r - action.src.r
    dir_c = action.dst.c - action.src.c
    return f"{action.src.r},{action.src.c}+{dir_r},{dir_c}"


def valid(x, y, n, m):
    """Check if the coordinates are in bounds.

    :param x:
    :param y:
    :param n:
    :param m:
    :return:
    """

    return 0 <= x < n and 0 <= y < m


def get_action_space(board_length=10, board_width=10):
    """Generates all possible actions for a piece in the game of checkers.

    :param board_length:
    :param board_width:
    :return:
    """

    all_actions_list = []

    for i in range(board_length):
        for j in range(board_width):
            moves_direction = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
            for move_dir in moves_direction:
                for r in range(1, 10):
                    dir_i = move_dir[0] * r
                    dir_j = move_dir[1] * r
                    if valid(i + dir_i, j + dir_j, board_length, board_width):
                        action = f"{i},{j}+{dir_i},{dir_j}"
                        all_actions_list.append(action)
    return all_actions_list


def evaluate(game):
    """Calculates the value of the end game from the maximizer player point of view.

    :param game:
    :return: the value of the end game
    :rtype: int
    """

    cnt = 0
    for piece in game.white_pieces:
        if piece.dead:
            cnt += 1
    if len(game.white_pieces) == cnt:
        return -1

    cnt = 0
    for piece in game.black_pieces:
        if piece.dead:
            cnt += 1

    if len(game.black_pieces) == cnt:
        return 1

    return 0


def load_best_model() -> tk.models.Model:
    """loads the current version of AlphaZero model.

    :return: AlphaZero neural network
    """

    print(f'loading version {config.CURRENT_VERSION}')

    model = build_alphazero_model((10, 10, 25), len(get_action_space()), 8, 64, config.REG_CONST)

    if config.CURRENT_VERSION is not None:
        model.load_weights(weights_folder + 'best alphazero' + f" {config.CURRENT_VERSION:0>3}" + '.h5')

    model.compile(loss={'value_head': 'mean_squared_error',
                        'policy_head': softmax_cross_entropy_with_logits},
                  optimizer=tk.optimizers.Adam(lr=config.LEARNING_RATE),
                  loss_weights={'value_head': 0.5, 'policy_head': 0.5})

    return model


def save_model(model: tk.models.Model, name='alphazero', version=1):
    model.save_weights(weights_folder + name + f" {version:0>3}" + '.h5')


class GameState:

    def __init__(self, game: Game):
        self.white_pieces = game.white_pieces
        self.black_pieces = game.black_pieces
        self.turn = game.current_turn
        self.board_length = game.grid.n
        self.board_width = game.grid.m
        self.terminal = game.end()
        self.game_class = game.__class__

    def get_all_possible_states(self):
        actions, states = self.game_class.build(self.white_pieces, self.black_pieces,
                                                self.turn).get_all_possible_states()
        ret = [GameState(state) for state in states]
        return actions, ret

    def get_game(self):
        return self.game_class.build(self.white_pieces, self.black_pieces, self.turn)

    def get_player_turn(self):
        return self.turn

    def is_terminal(self):
        return self.terminal

    def __eq__(self, other):
        if isinstance(other, GameState):
            my_pieces = self.white_pieces + self.black_pieces
            other_pieces = other.white_pieces + other.black_pieces
            if my_pieces == other_pieces and self.turn == other.turn:
                return True
        return False

    def __hash__(self):
        my_pieces = self.white_pieces + self.black_pieces
        hashable = tuple()
        for piece in my_pieces:
            hashable = hashable + (piece,)
        hashable = hashable + (self.turn,)
        return hash(hashable)


class StateStack:
    """A stack for saving playing history
    """

    def __init__(self):
        self.head = None
        self.max_len = 5  # turns history
        self.max_features = 5  # pieces planes (2 men) (2 kings) (1 turn flag)
        self.dq = deque(maxlen=self.max_len)

    def get_input_shape(self):
        return self.head.board_length, self.head.board_width, self.max_features * self.max_len

    def get_deep_representation_stack(self):
        # initialize the image stack with zeros
        ret = np.zeros(self.get_input_shape())

        # for each turn history we mask it as a numpy array
        for idx, state in enumerate(reversed(self.dq)):
            # we join the board pieces in one list for the ease of implementation
            pieces = state.white_pieces + state.black_pieces
            # calculates the index of the turn planes as each turn is defined as 5 planes
            idx *= self.max_features

            for piece in pieces:
                row = piece.cell.r
                column = piece.cell.c

                color_idx = 0 if piece.color == Color.WHITE else 1

                if piece.type == Type.KING:
                    # Mask the king pieces in (2, 4) planes for the (white, black) players respectively
                    ret[row][column][color_idx + idx + 2] = 1
                else:
                    # Mask the pawn pieces in (1, 3) planes for the (white, black) players respectively
                    ret[row][column][color_idx + idx] = 1

            # Mask the turn flag in the last plane (5) of the turn planes
            ret[0][0][idx + 4] = state.turn

        return ret

    def push(self, state: GameState):
        self.dq.append(state)
        self.head = state

    def __repr__(self):
        return self.dq.__repr__()


class ActionEncoder(LabelEncoder):
    """A utility to transform the action labels to unique integers and vice versa
    """
    def __init__(self):
        super().__init__()
        self.space_shape = 0

    def fit(self, action_space_list):
        self.space_shape = np.array(action_space_list).shape
        super().fit_transform(action_space_list)


class SampleBuilder:
    def __init__(self):
        self.samples = deque(maxlen=50000)
        self.moves = []

    def add_move(self, state_stack: StateStack, pi: np.array):
        self.moves.append({'state': state_stack, 'policy': pi})

    def commit_sample(self, value: int, pov: int):
        """Saves the game sample.

        :param value: the evaluation of the end game
        :param pov: the evaluation point of view
        :return:
        """
        for sample in self.moves:
            sample['value'] = value if sample['state'].head.turn == pov else -value
            self.samples.append(sample)
        self.moves.clear()

    def save(self, version: int):
        """write the samples as a dataset file to the archive folder.

        :param version: the dataset version
        :return:
        """
        with open(archive_folder + "dataset " + str(version).zfill(4) + ".pk", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(version: int):
        """loads a specific version of the datasets in the archive folder
        :param version: the dataset version
        :return:
        """
        with open(archive_folder + "dataset " + str(version).zfill(4) + ".pk", "rb") as f:
            return pickle.load(f)
