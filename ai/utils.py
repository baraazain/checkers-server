from collections import deque

import numpy as np
from sklearn.preprocessing import LabelEncoder

from model.game import Action, Game
from model.piece import Color, Type


def to_label(action: Action):
    dir_r = action.dst.r - action.src.r
    dir_c = action.dst.c - action.src.c
    return f"{action.src.r},{action.src.c}+{dir_r},{dir_c}"


def valid(x, y, n, m):
    return 0 <= x < n and 0 <= y < m


def get_action_space(board_length=10, board_width=10):
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


class GameState:
    """description of class"""

    def __init__(self, game: Game):
        self.white_pieces = game.white_pieces
        self.black_pieces = game.black_pieces
        self.turn = game.current_turn
        self.board_length = game.grid.n
        self.board_width = game.grid.m
        self.terminal = game.end()
        self.cls = game.__class__

    def get_all_possible_states(self):
        actions, states = self.cls.build(self.white_pieces, self.black_pieces, self.turn).get_all_possible_states()
        ret = [GameState(state) for state in states]
        return actions, ret

    def get_player_turn(self):
        return self.turn

    def is_terminal(self):
        return self.terminal


class StateStack:
    def __init__(self, initial_state: GameState):
        self.head = initial_state
        self.max_len = 5  # turns history
        self.max_features = 5  # pieces planes (2 men) (2 kings) (1 movable pieces)
        self.dq = deque(maxlen=self.max_len)
        self.dq.append(initial_state)

    def get_input_shape(self):
        return self.head.board_length, self.head.board_width, self.max_features * self.max_len

    def get_deep_representation_stack(self):
        ret = np.zeros(self.get_input_shape())
        for idx, state in enumerate(reversed(self.dq)):

            pieces = state.white_pieces + state.black_pieces

            idx *= self.max_features
            for piece in pieces:
                row = piece.cell.r
                column = piece.cell.c
                color_idx = 0 if piece.color == Color.WHITE else 1

                if piece.type == Type.KING:
                    ret[row][column][color_idx + idx + 2] = 1
                else:
                    ret[row][column][color_idx + idx] = 1

                if state.turn == 1 and piece.color == Color.WHITE:
                    ret[row][column][idx + 4] = 1
                if state.turn == 2 and piece.color == Color.BLACK:
                    ret[row][column][idx + 4] = 1

        return ret

    def push(self, state: GameState):
        self.dq.append(state)
        self.head = state

    def __repr__(self):
        return self.dq.__repr__()


class ActionEncoder(LabelEncoder):
    def __init__(self):
        super().__init__()
        self.space_shape = 0

    def fit(self, action_space_list):
        self.space_shape = np.array(action_space_list).shape
        super().fit_transform(action_space_list)


class SampleBuilder:
    def __init__(self):
        self.samples = []
        self.moves = []

    def commit_move(self, state_stack: StateStack, pi: np.array):
        self.moves.append({'state': state_stack, 'policy': pi})

    def commit_sample(self, value, pov):
        for sample in self.moves:
            sample['value'] = value if sample['state'].head.turn == pov else -value
            self.samples.append(sample)
        self.moves.clear()
