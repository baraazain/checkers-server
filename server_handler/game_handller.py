import datetime
from sqlite3.dbapi2 import Date

from ai.agent import *
from model.game import *
from model.turkish_game import TurkishGame
from server_handler.helper import *
from model.international_game import *
import json


def save_game_handle(_id, player):
    players: list = load_players()
    state = False
    for p in players:
        if p.id == player.id:
            p.games_id_saved.append(_id)
            state = True
    save_players(players)
    return state


def show_games_save_handle(player):
    players: list = load_players()
    games = []
    for p in players:
        if p.id == player.id:
            for _id in p.games_id_saved:
                games.append(get_game_by_id(_id))
    if games:
        return games
    else:
        return None


def load_game_handle(_id):
    print(type(id))
    if get_game_by_id(_id) is not None:
        print("fuck")
        game = get_game_by_id(_id)
        return game
    else:
        return None


def create_new_game_handle(game_info: GameInfo, all_game_playing, player1):
    id = len(all_game_playing)

    player2 = None
    if game_info.level == Level.HUMAN:
        player2 = None
    elif game_info.level == Level.DUMMY:
        player2 = DummyAgent()
    elif game_info.level == Level.MONTE_CARLO:
        player2 = MonteCarloAgent(3)
    elif game_info.level == Level.ALPHA_BETA:
        player2 = MiniMaxAgent(1, 5)
    elif game_info.level == Level.ALPHA_ZERO:
        player2 = AlphaZero(4)

    game = None
    if game_info.mode == Mode.INTERNATIONAL:
        game = InternationalGame(id, player2, player2, datetime.datetime.now())
    elif game_info.mode == Mode.TURKISH:
        game = TurkishGame(id, player2, player2, datetime.datetime.now())

    return game


def initialize_game_handle(game: Game):
    game.init()
    return game


def get_possible_moves_handle(game, piece):
    paths = game.get_all_possible_paths()
    # print("Start Pathssssss")
    # for path in paths:
    #     print("\tStart Path")
    #     for action in path:
    #         print("\t\t", action)
    #     print("\tEnd Path")
    # print("End Pathssssss")
    actions = []
    for path in paths:
        first_piece = game.validate_action(path[0]).src.piece
        # print("FirstCell: ", path[0].src)
        # print("FirstPiece: ", game.validate_action(path[0]).src.piece)
        if first_piece == piece:
            new_path = [(piece.cell.r, piece.cell.c)]
            for action in path:
                new_path.append((action.dst.r, action.dst.c))
            actions.append(path)

    return actions


def compatible(path, actions):
    if len(path) != len(actions):
        return False

    for i in range(0, len(path), 1):
        (src, dst) = actions[i]

        if src != path[i].src or dst != path[i].dst:
            return False

    return True


def get_new_pairs(game, pairs):
    new_pairs = [pairs[0]]

    cur_dir_r = pairs[1][0] - pairs[0][0]
    cur_dir_c = pairs[1][1] - pairs[0][1]

    should_take = False
    for i in range(1, len(pairs) - 1, 1):
        (r1, c1) = pairs[i - 1]
        (r2, c2) = pairs[i]

        dir_r = r2 - r1
        dir_c = c2 - c1

        print("DIRRR: ", dir_r, dir_c, cur_dir_r, cur_dir_c)

        piece1 = game.grid[r1][c1].piece
        piece2 = game.grid[r2][c2].piece

        if dir_r != cur_dir_r or dir_c != cur_dir_c:
            new_pairs.append(pairs[i - 1])
            should_take = False
        if piece2 is not None and should_take:
            new_pairs.append(pairs[i - 1])
        if piece2 is not None:
            should_take = True

        cur_dir_r = dir_r
        cur_dir_c = dir_c

    new_pairs.append(pairs[len(pairs) - 1])

    return new_pairs


def get_path(game, pairs):
    new_pairs = get_new_pairs(game, pairs)

    print("Start new_pairs")
    for (r, c) in new_pairs:
        print(r, c)
    print("End new_pairs")

    print("LEN: ", len(new_pairs))
    actions = []
    for i in range(1, len(new_pairs), 1):
        (r1, c1) = new_pairs[i - 1]
        (r2, c2) = new_pairs[i]

        print("1: ", r1, c1)
        print("2: ", r2, c2)
        src: Cell = game.grid[r1][c1]
        dst: Cell = game.grid[r2][c2]

        actions.append((src, dst))

    all_paths = game.get_all_possible_paths()

    for (r, c) in actions:
        print(r, c)

    for path in all_paths:
        print("STARTT")
        for action in path:
            print(action)
        if compatible(path, actions):
            print("COMPATIBLE")
            return path
        print("ENDD")

    return None


def apply_action_handle(game, path):
    game.apply_turn(path)
    return game


def undo_handle(game):
    game.undo()
    return game


def join_handle(game, player):
    game.player2 = player
    return game
