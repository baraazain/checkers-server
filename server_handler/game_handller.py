from server_handler.helper import *


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
