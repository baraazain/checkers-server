from model.game import GameState, King, Position, Action
from .config import MAXIMIZER
from collections import deque
from copy import deepcopy
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


def mirror_coordinates(board_length, board_width, x, y):
        return board_length + 1 - x, board_width + 1 - y

    
def mirror_action(action: Action, board_length=10, board_width=10):
    src_mirror_x, src_mirror_y = mirror_coordinates(board_length, board_width, 
                                                    action.src.row + 1, action.src.column + 1)
    src_mirror_x -= 1
    src_mirror_y -= 1

    dst_mirror_x, dst_mirror_y = mirror_coordinates(board_length, board_width, 
                                                    action.dst.row + 1, action.dst.column + 1)
    dst_mirror_x -= 1
    dst_mirror_y -= 1
        
    return Action(Position(src_mirror_x, src_mirror_y), Position(dst_mirror_x, dst_mirror_y), action.player)


def to_label(action: Action):
    dir_r = action.dst.row - action.src.row
    dir_c = action.dst.column - action.src.column
    return f"{action.src.row},{action.src.column}+{dir_r},{dir_c}"


def to_action(action: str):
    pos_str, dir_str = action.split("+")
    src_x , src_y = pos_str.split(",")
    src_x = int(src_x)
    src_y = int(src_y)

    dir_x, dir_y = dir_str.split(",")
    dir_x = int(dir_x)
    dir_y = int(dir_y)

    dst_x = src_x + dir_x
    dst_y = src_y + dir_y
    return Position(src_x, src_y),Position(dst_x, dst_y)


def valid(x, y, n, m):
    return 0 <= x < n and 0 <= y < m


def get_action_space(board_length, board_width):
    all_list_action = []

    for i in range(board_length):
        for j in range(board_width):
            moves_direction = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
            for move_dir in moves_direction:
                for r in range(1, 10):
                    dir_i = move_dir[0] * r
                    dir_j = move_dir[1] * r
                    if valid(i + dir_i, j + dir_j, board_length, board_width):
                        action = f"{i},{j}+{dir_i},{dir_j}"
                        all_list_action.append(action)
    return all_list_action

class StateStack:
    def __init__(self,inital_state: GameState):
        self.head = inital_state
        self.max_len = 5 # turns history
        self.max_features = 4 # pieces planes (2 men) (2 kings)
        self.dq = deque(maxlen=self.max_len)
        self.dq.append(inital_state)
        

    def mirror_pieces(self, all_pieces):
        ret = []
        for piece in all_pieces:
            if not piece.dead:
                x, y = mirror_coordinates(self.head.board_length, self.head.board_width,
                                               piece.position.row + 1, piece.position.column + 1)
                piece_copy = deepcopy(piece)
                piece_copy.position = Position(x - 1, y - 1)
                ret.append(piece)
        return ret
    
    def get_input_shape(self):
        return (self.head.board_length, self.head.board_width, self.max_features * self.max_len)

    def get_deep_representation_stack(self):
        ret = np.zeros((self.head.board_length, self.head.board_width, self.max_features * self.max_len))
        for idx, state in enumerate(reversed(self.dq)):
            
            pawns = state.white_pawn_list + state.black_pawn_list
            
            if self.head.get_player_turn() != MAXIMIZER:
                pawns = self.mirror_pieces(pawns)

            idx *= self.max_features
            for pawn in pawns:
                if not pawn.dead:
                    row = pawn.position.row
                    column = pawn.position.column
                    if self.head.get_player_turn() == MAXIMIZER:
                        color_idx = 0 if pawn.color[0] == "W" else 1
                    else:
                        color_idx = 0 if pawn.color[0] == "B" else 1
                    
                    if isisinstance(pawn , King):
                        ret[row][column][color_idx + idx + 2] = 1
                    else:
                        ret[row][column][color_idx + idx] = 1
        return ret
    
    def push(self, state):
        self.dq.append(state)
        self.head = state

    def __repr__(self):
        return self.dq.__repr__()

class ActionEncoder():
    def __init__(self):
        self.lable_encoder = LabelEncoder()
        self.onehot_encoder = OneHotEncoder(sparse=False)
        
        
    def fit(self, action_space_list):
        self.space_shape = len(action_space_list)
        action_space_list = self.lable_encoder.fit_transform(action_space_list)
        action_space_list = action_space_list.reshape(self.space_shape, 1)
        self.onehot_encoder.fit(action_space_list)
        
        
    def onehot_transform(self, data):
        data = self.lable_transform(data)
        data = data.reshape(len(data), 1)
        data = self.onehot_encoder.transform(data)
        return data

    
    def onehot_inverse_transform(self, data):
        data = self.onehot_encoder.inverse_transform(data)
        data = self.lable_encoder.inverse_transform(data.ravel())
        return data

    def label_transform(self, data):
        return self.lable_encoder.transform(data)
    
    def label_inverse_transform(self, data):
        return self.lable_encoder.inverse_transform(data.ravel())
    
    """
    def onehot_inverse_transform(self, data):
        data = self.inverse_transform(data)
        ret = []
        for action in data:
            ret.append(to_action(action))
        return ret
    """


class SampleBuilder:
    def __init__(self):
        self.samples = []
        self.moves = []
    def commit_move(self, state_stack: StateStack, pi: np.array):
        self.moves.append({'state':state_stack, 'policy':pi})
    def commit_sample(self, value, pov):
        for sample in self.moves:
            sample['value'] = value if sample['state'].head.get_player_turn() == pov else -value
            self.samples.append(sample)
        self.moves.clear()

