import datetime
from sqlite3.dbapi2 import Date

from ai.agent import *
from model.game import *
from model.turkish_game import TurkishGame
from server_handler.helper import *
from model.international_game import *
import json


def save_game_handle(_id, player):
    players = load_players()
    state = False
    for p in players:
        if p.name == player.name:
            p.games_id_saved.append(_id)
            state = True
    save_players(players)
    return state


def show_games_save_handle(p):
    player = get_player_by_name(p)
    id_games = player.games_id_saved
    games = []
    for i in id_games:
        games.append(get_game_by_id(i))
    if len(games) > 0:
        return games
    else:
        return None


def load_game_handle(_id):
    if get_game_by_id(_id):
        game = get_game_by_id(_id)
        return game
    else:
        return None


def create_new_game_handle(game_info: GameInfo, all_game_playing, player1):
    id = len(all_game_playing)

    player2 = None
    if game_info.level == Level.HUMAN:
        pass
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
    paths = game.get_all_possible_actions()
    actions = []
    for path in paths:
        first_piece = path[0].src.piece
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


def get_path(game, pairs):
    print("LEN: ", len(pairs))
    actions = []
    for i in range(1, len(pairs), 1):
        (r1, c1) = pairs[i - 1]
        (r2, c2) = pairs[i]

        print("1: ", r1, c1)
        print("2: ", r2, c2)
        src: Cell = game.grid[r1][c1]
        dst: Cell = game.grid[r2][c2]

        actions.append((src, dst))

    all_paths = game.get_all_possible_actions()

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