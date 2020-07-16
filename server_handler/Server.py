import asyncio
import datetime

from server_handler.ResponseResult import Result
from server_handler.game_handller import *
from server_handler.auth_handler import *
from server_handler.contest_handler import *
from model.actors import *
from model.utils import *
from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

all_player_connecting = {}


@sio.event
async def connect(sid, environ):
    print('connected: ', sid)


@sio.event
async def disconnect(sid):
    print('disconnected: ', sid)
    player = get_player_by_sid(sid, all_player_connecting)
    del all_player_connecting[player.id]


@sio.event
async def signup(sid, player):
    p: RemotePlayer = signup_handle(player)
    p.sid = sid
    if p is not None:
        result = Result(True, 'successful signup', None)
        all_player_connecting[p.id] = p
        await sio.emit("signup_result", to_json(result))
    else:
        result = Result(False, 'failed signup <user name taken>', None)
        await sio.emit("signup_result", to_json(result))


@sio.event
async def login(sid, player):
    p: RemotePlayer = login_handle(player)
    p.sid = sid
    if p is not None:
        result = Result(True, 'successful login', None)
        all_player_connecting[p.id] = p
        await sio.emit("login_result", to_json(result))
    else:
        result = Result(False, 'failed username or password is wrong', None)
        await sio.emit("login_result", to_json(result))


@sio.event
async def update_account(sid, update_player):
    p: RemotePlayer = update_account_handle(get_player_by_sid(sid), update_player)
    p.sid = sid
    if p is not None:
        all_player_connecting[p.id] = p
        result = Result(True, 'successful update', None)
        await sio.emit("update_account_result", to_json(result))
    else:
        result = Result(False, 'cant update try again', None)
        await sio.emit("update_account_result", to_json(result))


@sio.event
async def remove_account(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    if remove_account_handle(player):
        del all_player_connecting[player.id]
        result = Result(True, 'successful delete', None)
        await sio.emit("remove_account_result", to_json(result))
    else:
        result = Result(False, "can't delete the account try again please", None)
        await sio.emit("remove_account_result", to_json(result))


@sio.event
async def show_account(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    p = show_account_handle(player)
    if p:
        result = Result(True, "successful", p)
        await sio.emit("show_account_result", to_json(result))
    else:
        result = Result(False, "can't show the account try again please", None)
        await sio.emit("show_account_result", to_json(result))


async def manage_contest(contest: Contest):
    await sio.emit("notify_round_participants", "test", room=contest.id)
    contest.distribute()
    if contest.is_end():
        winner: Player = contest.participants[0]
        print("The Winner is: " + winner.name + " " + winner.id)
        return

    @sio.on(f"ababa_{contest.id}")
    async def disqualify(sid, data):
        pass

    contest.current_game = 0
    while not contest.is_round_end():
        game = contest.games[contest.current_game]
        game.start_game()
        contest.current_game += 1
        # game.start_game(self)

        # remove losers from contest room
    contest.participants = contest.get_qualified_players()
    await manage_contest(contest)


async def start_contest(contest):
    await sio.emit('create_contest')
    await manage_contest(contest)


@sio.event
async def create_contest(sid, form):
    contest = create_contest_handler(form)
    if contest:
        asyncio.create_task(run_at(contest.date, start_contest(contest)))
        result = Result(True, "successful", contest)
        await sio.emit("create_contest_result", to_json(result))
    else:
        result = Result(False, "can not create contest try again", None)
        await sio.emit("create_contest_result", to_json(result))


@sio.event
async def join_player_to_contest(sid, _id):
    player = get_player_by_sid(sid, all_player_connecting)
    res = join_player_to_contest_handler(_id, player)
    if res:
        sio.enter_room(sid, id)
        result = Result(True, "successful", res)
        await sio.emit("join_player_to_contest_result", to_json(result))
    else:
        result = Result(False, "can not join you should to take due in full constraints", None)
        await sio.emit("join_player_to_contest_result", to_json(result))


@sio.event
async def show_all_contest_available(sid):
    res = show_all_contest_available_handler()
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_all_contest_available_result", to_json(result))
    else:
        result = Result(False, "do not exist any contest in server", None)
        await sio.emit("show_all_contest_available_result", to_json(result))


@sio.event
async def show_my_contests_finished(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    res = show_finish_contest_handler(player)
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_my_contests_finished_result", to_json(result))
    else:
        result = Result(False, "can't show the contest finished try again please", None)
        await sio.emit("show_my_contests_finished_result", to_json(result))


@sio.event
async def show_my_current_contest(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    res = show_my_current_contest(player)
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_my_current_contest_result", to_json(result))
    else:
        result = Result(False, "can't show the current contest try again please", None)
        await sio.emit("show_my_current_contest_result", to_json(result))


@sio.event
async def save(sid, _id):
    player = get_player_by_sid(sid, all_player_connecting)
    res = save_game_handle(_id, player)
    if res:
        result = Result(True, "save is completed", None)
        await sio.emit("save_result", to_json(result))
    else:
        result = Result(False, "can't save this game try again please", None)
        await sio.emit("save_result", to_json(result))


@sio.event
async def show_games_saved(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    res = show_games_save_handle(player)
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("show_games_saved_result", to_json(result))
    else:
        result = Result(False, "don't have any games saved", None)
        await sio.emit("show_games_saved_result", to_json(result))


@sio.event
async def load(sid, _id):
    player = get_player_by_sid(sid, all_player_connecting)
    res = load_game_handle(_id, player)
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("load_result", to_json(result))
    else:
        result = Result(False, "n't load this game", None)
        await sio.emit("load_result", to_json(result))


if __name__ == '__main__':
    web.run_app(app, host="localhost", port=8080)
