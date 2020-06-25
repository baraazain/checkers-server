from server_handler.ResponseResult import Result
from server_handler.game_handller import *
from server_handler.auth_handler import *
from model.actors import *
from model.utils import *
from aiohttp import web
import socketio
import json

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

all_player_connecting = {}
all_game_playing = {}


# TODO: needs to debug the module

@sio.on('player_connect')
async def player_connect(sid, player):
    pp = RemotePlayer.from_dict(json.loads(player))
    player = get_player_by_name(pp.name)
    all_player_connecting[player.name].name = player.name
    all_player_connecting[player.name].password = player.password
    all_player_connecting[player.name].sid = player.sid


@sio.event
async def connect(sid, environ):
    print('connected: ', sid)
#   await sio.emit("login", room=sid)


@sio.event
async def message(sid, data):
    print(sid, 'say: ', data)


@sio.event
async def json_message(sid, data):
    s = json.loads(data)
    print(s)
    print('json data as a python object')
    print(Piece.from_dict(s))


@sio.event
async def json_message1(sid, data):
    s = json.loads(data)
    print(s)
    print('json data as a python object')
    print(RemotePlayer.from_dict(s))


@sio.event
async def disconnect(sid):
    print('disconnected: ', sid)
#    player = get_player_by_sid(sid, all_player_connecting)
#    del all_player_connecting[player.name]


@sio.on('signup')
async def signup(sid, player):
    p = RemotePlayer().from_dict(json.loads(player))
    p.sid = sid
    if signup_handle(player):
        result = Result(True, 'successful signup', None)
        all_player_connecting[p.name].name = p.name
        await sio.emit("signklup", to_json(result))
    else:
        result = Result(False, 'failed signup <user name taken>', None)
        await sio.emit("signup", to_json(result))


@sio.on('login')
async def login(sid, player):
    p = RemotePlayer().from_dict(json.loads(player))
    p.sid = sid
    if login_handle(player):
        result = Result(True, 'successful login', None)
        all_player_connecting[p.name].name = p.name
        await sio.emit("login", to_json(result))
    else:
        result = Result(False, 'failed username or password is wrong', None)
        await sio.emit("login", to_json(result))


@sio.on('update_account')
async def update_account(sid, update_player):
    if update_account_handle(update_player):
        all_player_connecting[update_player.id].name = update_player.name
        all_player_connecting[update_player.id].password = update_player.password
        result = Result(True, 'successful update', None)
        await sio.emit("update_account", to_json(result))
    else:
        result = Result(False, 'cant update try again', None)
        await sio.emit("update_account", to_json(result))


@sio.on('remove_account')
async def remove_account(sid, player):
    if remove_account_handle(player):
        del all_player_connecting[player.id]
        result = Result(True, 'successful delete', None)
        await sio.emit("remove_account", to_json(result))
    else:
        result = Result(False, "can't delete the account try again please", None)
        await sio.emit("remove_account", to_json(result))


@sio.on('show_account')
async def show_account(sid, player):
    res = show_account_handle(player)
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_account", to_json(result))
    else:
        result = Result(False, "can't show the account try again please", None)
        await sio.emit("show_account", to_json(result))


@sio.on('save')
async def save(sid, _id):
    player = get_player_by_sid(sid)
    res = save_game_handle(_id, player)
    if res:
        result = Result(True, "save is completed", None)
        await sio.emit("save", to_json(result))
    else:
        result = Result(False, "can't save this game try again please", None)
        await sio.emit("save", to_json(result))


@sio.on('show_games_saved')
async def show_games_saved(sid):
    player = get_player_by_sid(sid)
    res = show_games_save_handle(player)
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("show_games_saved", to_json(result))
    else:
        result = Result(False, "don't have any games saved", None)
        await sio.emit("show_games_saved", to_json(result))


@sio.on('load')
async def load(sid, _id):
    player = get_player_by_sid(sid)
    res = load_game_handle(_id, player)
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("load", to_json(result))
    else:
        result = Result(False, "n't load this game", None)
        await sio.emit("load", to_json(result))


if __name__ == '__main__':
    web.run_app(app, host="localhost", port=8080)
