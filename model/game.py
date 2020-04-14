from math import log10, floor
from copy import deepcopy


class Position:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def __str__(self):
        return "(" + str(self.row + 1) + ", " + str(self.column + 1) + ")"


class Cell(Position):
    def __init__(self, row, column, content):
        Position.__init__(self, row, column)
        self.content = content

    #    def __str__(self):
    #        return Position.__str__(self) + " " + str(self.content)

    def _dist_row(self, other):
        return abs(self.row - other.row)

    def _dist_column(self, other):
        return abs(self.column - other.column)

    def dist(self, other, axis=0):
        if axis == 0:
            return self._dist_row(other)
        else:
            return self._dist_column(other)


class Piece:
    def __init__(self, kind, piece_id, color):
        self.kind = kind
        self.id = piece_id
        self.color = color
        self.dead = False

    def __str__(self):
        return self.color + " " + self.kind + str(self.id)


class Pawn(Piece):
    def __init__(self, piece_id, color):
        Piece.__init__(self, "Pawn", piece_id, color)


class King(Piece):
    def __init__(self, piece_id, color):
        Piece.__init__(self, "King", piece_id, color)


class Grid:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.cnt_row = floor(log10(n)) + 1
        self.cnt_column = floor(log10(m)) + 1
        self.grid = [[Cell(i, j, None) for j in range(self.m)] for i in range(self.n)]

    def __str__(self):
        ret = str.center(" ", self.cnt_row + 2)
        for i in range(self.m):
            ret += str.center(str(i + 1), self.cnt_column + 1)
        ret += "\n"
        for i in range(self.n):
            ret += str.center(str(i + 1) + "|", self.cnt_row + 2)
            for j in range(self.m):
                if self.grid[i][j].content is None:
                    ret += str.center(".", self.cnt_column + 1)
                else:
                    p = self.grid[i][j].content
                    ret += str.center(p.color[0], self.cnt_column + 1)
            ret += "\n"
        return ret

    def __getitem__(self, item):
        return self.grid[item]

    def _valid(self, row, column):
        return 0 <= row < self.n and 0 <= column < self.m

    def valid(self, cell):
        return self._valid(cell.row, cell.column)


class Player:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password
        self.current_contests = []
        self.rate = 1000

    def act(self, game):
        pass


class Action:
    def __init__(self, src, dst, player):
        self.src = src
        self.dst = dst
        self.player = player
        self.eat = None
        self.id = -1

    def get_type(self):
        return 1 if abs(self.src.row - self.dst.row) == 1 else 2

    def __str__(self):
        return str(self.src) + " -> " + str(self.dst)


class Mode:
    INTERNATIONAL = "INTERNATIONAL"
    SYRIAN = "SYRIAN"


def _check_king(action):
    src = action.src
    dst = action.dst

    if src.dist(dst, 0) != src.dist(dst, 1):
        return False, None, None, None, None

    dir_row = (dst.row - src.row) // src.dist(dst, axis=0)
    dir_column = (dst.column - src.column) // src.dist(dst, axis=1)

    cur_row = src.row + dir_row
    cur_column = src.column + dir_column

    return True, dir_row, dir_column, cur_row, cur_column


class GameState:
    def __init__(self, player1, player2):
        self.board_length = 10
        self.board_width = 10
        self.board = Grid(10, 10)
        self.white_pawn_list = []
        self.black_pawn_list = []
        self.turn = 0
        self.white_dead = 0
        self.black_dead = 0
        self.players_list = [player1, player2]
        self.mode = Mode.INTERNATIONAL
        

    def init(self):
        self.possible_actions = None
        self.black_dead = self.white_dead = 0
        cnt = 1
        for i in range(4):
            for j in range(1 - (i % 2), 10, 2):
                p = Pawn(cnt, "Black")
                p.position = Position(i, j)
                self.board[i][j].content = p
                self.black_pawn_list.append(p)
                cnt += 1
        cnt = 1
        for i in range(6, 10):
            for j in range(1 - (i % 2), 10, 2):
                p = Pawn(cnt, "White")
                p.position = Position(i, j)
                self.board[i][j].content = p
                self.white_pawn_list.append(p)
                cnt += 1

    def print_board(self):
        print(self.board)

    def get_player_turn(self):
        return self.turn % 2

    def get_current_player(self) -> Player:
        return self.players_list[self.get_player_turn()]

    def get_current_player_character(self):
        turn = self.get_player_turn()
        return "W" if turn == 0 else "B"

    def get_piece(self, row, column):
        return self.board[row][column].content

    def _correct_king_walk(self, action: Action):
        correct, dir_row, dir_column, cur_row, cur_column = _check_king(action)

        if not correct:
            return False

        while cur_row != action.dst.row:
            if self.get_piece(cur_row, cur_column) is not None:
                return False
            cur_row += dir_row
            cur_column += dir_column

        return True

    def _correct_king_eat(self, action: Action):
        correct, dir_row, dir_column, cur_row, cur_column = _check_king(action)

        if not correct:
            return False

        cnt = 0
        while cur_row != action.dst.row:
            piece = self.get_piece(cur_row, cur_column)
            if piece is not None:
                cnt += 1
                if piece.color[0] == action.src.content.color[0]:
                    return False
            cur_column += dir_column
            cur_row += dir_row

        return cnt == 1

    def _correct_walk(self, action: Action):
        src = action.src
        dst = action.dst
        if not self.board.valid(src):
            return False
        if not self.board.valid(dst):
            return False
        if src.content is None:
            return False
        if dst.content is not None:
            return False
        if isinstance(src.content, King):
            return self._correct_king_walk(action)

        r = src.row
        c = src.column
        ac = [-1, 1]

        if src.content.color[0] == 'W':
            ar = [-1, -1]
            for i in range(2):
                nr = r + ar[i]
                nc = c + ac[i]

                if nr == dst.row and nc == dst.column:
                    return True
        elif src.content.color[0] == "B":
            ar = [1, 1]
            for i in range(2):
                nr = r + ar[i]
                nc = c + ac[i]
                if nr == dst.row and nc == dst.column:
                    return True
        return False

    def _correct_eat(self, action: Action):
        src = action.src
        dst = action.dst

        if not self.board.valid(src):
            return False
        if not self.board.valid(dst):
            return False
        if src.content is None:
            return False
        if dst.content is not None:
            return False
        if isinstance(src.content, King):
            return self._correct_king_eat(action)

        if src.dist(dst, axis=0) != 2 or src.dist(dst, axis=1) != 2:
            return False

        middle_row = (src.row + dst.row) // 2
        middle_column = (src.column + dst.column) // 2

        if self.get_piece(middle_row, middle_column) is None:
            return False
        if self.get_piece(middle_row, middle_column).color[0] == src.content.color[0]:
            return False

        return True

    def _get_all_possible_walks(self, src):
        actions = []
        current_player = self.get_current_player()
        for i in range(self.board_length):
            for j in range(self.board_width):
                if i != src.row and j != src.column:
                    action = Action(self.board[src.row][src.column], self.board[i][j], current_player)
                    if self._correct_walk(action):
                        actions.append(action)
        return actions

    def _get_all_possible_eats(self, src):
        actions = []
        current_player = self.get_current_player()

        for i in range(self.board_length):
            for j in range(self.board_width):
                action = Action(self.board[src.row][src.column], self.board[i][j], current_player)
                if self._correct_eat(action):
                    actions.append(action)
        return actions

    def get_all_possible_actions(self):
        if self.possible_actions is not None:
            return self.possible_actions
        actions = []
        if self.get_player_turn() == 0:
            for piece in self.white_pawn_list:
                if not piece.dead:
                    actions.extend(action for action in self._get_all_possible_eats(self.board[piece.position.row][piece.position.column]))
            if len(actions) == 0:
                for piece in self.white_pawn_list:
                    if not piece.dead:
                        actions.extend(action for action in self._get_all_possible_walks(self.board[piece.position.row][piece.position.column]))
        else:
            for piece in self.black_pawn_list:
                if not piece.dead:
                    actions.extend(action for action in self._get_all_possible_eats(self.board[piece.position.row][piece.position.column]))
            if len(actions) == 0:
                for piece in self.black_pawn_list:
                    if not piece.dead:
                        actions.extend(action for action in self._get_all_possible_walks(self.board[piece.position.row][piece.position.column]))
        self.possible_actions = actions
        return actions

    def get_all_possible_states(self):
        states = []
        actions = self.get_all_possible_actions()
        for action in actions:
            new_state = deepcopy(self)
            new_state.apply_action(action)
            states.append(new_state)
        return actions, states 

    def is_legal_action(self, action):
        if self.get_player_turn() == 0 and self.get_piece(action.src.row, action.src.column).color[0] != "W":
            return False
        if self.get_player_turn() == 1 and self.get_piece(action.src.row, action.src.column).color[0] != "B":
            return False
        action = Action(self.board[action.src.row][action.src.column],
                        self.board[action.dst.row][action.dst.column],
                        self.get_current_player())
        return self._correct_walk(action) or self._correct_eat(action)

    def apply_action(self, action):
        self.possible_actions = None
        src = action.src
        dst = action.dst
        piece = self.get_piece(src.row, src.column)
        if isinstance(piece, King):
            self._apply_king_action(action)
            return

        self.board[src.row][src.column].content = None
        self.board[dst.row][dst.column].content = piece
        piece.position = Position(dst.row, dst.column)

        if self.get_player_turn() == 0 and dst.row == 0:
            king = King(piece.id, piece.color)
            king.position = Position(dst.row, dst.column)
            self.board[dst.row][dst.column].content = king
            self.white_pawn_list[piece.id - 1] = king

        elif self.get_player_turn() == 1 and dst.row == self.board_length - 1:
            king = King(piece.id, piece.color)
            king.position = Position(dst.row, dst.column)
            self.board[dst.row][dst.column].content = king
            self.black_pawn_list[piece.id - 1] = king

        if action.get_type() == 2:
            middle_row = (src.row + dst.row) // 2
            middle_column = (src.column + dst.column) // 2
            p = self.get_piece(middle_row, middle_column)
            p.dead = True
            action.eat = p
            if p.color[0] == "B":
                self.black_dead += 1
            else:
                self.white_dead += 1
            self.board[middle_row][middle_column].content = None
            if len(self._get_all_possible_eats(dst)) != 0:
                self.turn -= 1
        self.turn += 1
        return

    def _apply_king_action(self, action):
        src = action.src
        dst = action.dst

        p = self.get_piece(src.row, src.column)
        color = p.color[0]
        p.position = Position(dst.row, dst.column)

        self.board[dst.row][dst.column].content = p

        dir_r = (dst.row - src.row) // src.dist(dst, axis=0)
        dir_c = (dst.column - src.column) // src.dist(dst, axis=1)

        cur_r = src.row
        cur_c = src.column
        while cur_r != dst.row:
            p = self.get_piece(cur_r, cur_c)
            if p is not None:
                if p.color[0] != color:
                    action.eat = p
                    p.dead = True
            self.board[cur_r][cur_c].content = None

            cur_r += dir_r
            cur_c += dir_c

        if action.eat is not None:
            if action.eat.color[0] == "B":
                self.black_dead += 1
            else:
                self.white_dead += 1
            if len(self._get_all_possible_eats(dst)) != 0:
                self.turn -= 1

        self.turn += 1
        return

    def get_winner(self):
        if self.white_dead == len(self.white_pawn_list):
            return self.players_list[1]
        if self.black_dead == len(self.black_pawn_list):
            return self.players_list[0]
        return None
    
    #from the pov of maximizer
    def get_value(self):
        if self.white_dead == len(self.white_pawn_list):
            return -1
        if self.black_dead == len(self.black_pawn_list):
            return 1
        return 0
        

    def is_terminal(self):
        if self.white_dead == len(self.white_pawn_list) or self.black_dead == len(self.black_pawn_list):
            return True
        return len(self.get_all_possible_actions()) == 0

    def get_id(self):
        pass