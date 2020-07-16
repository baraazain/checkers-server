from server_handler.helper import *


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
            for id in p.games_id_saved:
                games.append(get_game_by_id(id))

    if len(games) > 0:
        return games
    else:
        return None


def load_game_handle(_id):
    if get_game_by_id(_id) is not None:
        game = get_game_by_id(_id)
        return game
    else:
        return None
