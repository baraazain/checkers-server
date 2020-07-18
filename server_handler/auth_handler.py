from model.actors import *
import json
from server_handler.helper import *


def signup_handle(playerx):
    player = RemotePlayer.from_dict(json.loads(playerx))
    players: list = load_players()
    for user in players:
        if player.name == user.name:
            return None

    if len(players) == 0:
        new_id = 1
    else:
        new_id = players[len(players) - 1].id + 1

    p = RemotePlayer(0, new_id, player.name, player.password)
    players.append(p)
    save_players(players)
    return p


def login_handle(playerx):
    player = RemotePlayer.from_dict(json.loads(playerx))
    players: list = load_players()
    for user in players:
        if player.name == user.name and player.password == user.password:
            return user
    return None


def update_account_handle(p,playerx):
    player = RemotePlayer.from_dict(json.loads(playerx))
    players = load_players()
    for user in players:
        if user.name == p.name and user.password== p.password:
            user.name = player.name
            user.password = player.password
            save_players(players)
            return user
    return None


def remove_account_handle(player):
    players: list = load_players()
    for user in players:
        if user.name == player.name and user.password==player.password:
            players.remove(user)
            save_players(players)
            return True
    return False


def show_account_handle(player):
    players = load_players()
    for user in players:
        if user.name == player.name and user.password==player.password:
            return user
    return None
