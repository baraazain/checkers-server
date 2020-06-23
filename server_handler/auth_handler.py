from model.actors import *
import json
from server_handler.helper import *


def signup_handle(player):
    player = RemotePlayer().from_dict(json.loads(player))
    players: list = load_players()
    state = False
    for user in players:
        if player.name == user.name:
            state = True

    if not state:
        p = RemotePlayer()
        p.name = player.name
        p.password = player.password
        players.append(p)
        save_players(players)
        return True
    else:
        return False


def login_handle(player):
    player = RemotePlayer().from_dict(json.loads(player))
    players: list = load_players()
    state = False
    for user in players:
        if player.name == user.name and player.password == user.password:
            state = True
    return state


def update_account_handle(playerx):
    player = RemotePlayer().from_dict(json.loads(playerx))
    players = load_players()
    state = False
    for user in players:
        if user.name == player.name:
            state = True
            user.name = player.name
            user.password = player.password
    save_players(players)
    return state


def remove_account_handle(playerx):
    player = RemotePlayer().from_dict(json.loads(playerx))
    players: list = load_players()
    state = False
    for user in players:
        if user.name == player.name:
            players.remove(user)
            state = True
    save_players(players)
    return state


def show_account_handle(playerx):
    player = RemotePlayer().from_dict(json.loads(playerx))
    players = load_players()
    for user in players:
        if user.name == player.name:
            return user
    return None
