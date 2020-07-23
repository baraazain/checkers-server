import copy
import asyncio
import threading
from typing import List

from model.game import *
from server_handler.Request import FirstButtonRequest, SecondButtonRequest, IdRequest, JoinRequest, WaitingGamesRequest
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
all_current_contests = {}
all_game_playing = {}
all_game_waiting = {}


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

    if p is not None:
        p.sid = sid
        result = Result(True, 'successful signup', None)
        all_player_connecting[p.id] = p
        await sio.emit("signup_result", to_json(result), to=sid)
    else:
        result = Result(False, 'failed signup <user name taken>', None)
        await sio.emit("signup_result", to_json(result), to=sid)


@sio.event
async def login(sid, player):
    p: RemotePlayer = login_handle(player)
    if p is not None:
        p.sid = sid
        result = Result(True, 'successful login', None)
        all_player_connecting[p.id] = p
        await sio.emit("login_result", to_json(result), to=sid)
    else:
        result = Result(False, 'failed username or password is wrong', None)
        await sio.emit("login_result", to_json(result), to=sid)


@sio.event
async def update_account(sid, update_player):
    p: RemotePlayer = update_account_handle(get_player_by_sid(sid, all_player_connecting), update_player)
    if p is not None:
        p.sid = sid
        all_player_connecting[p.id] = p
        result = Result(True, 'successful update', None)
        await sio.emit("update_account_result", to_json(result), to=sid)
    else:
        result = Result(False, 'cant update try again', None)
        await sio.emit("update_account_result", to_json(result), to=sid)


@sio.event
async def remove_account(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    if remove_account_handle(player):
        del all_player_connecting[player.id]
        result = Result(True, 'successful delete', None)
        await sio.emit("remove_account_result", to_json(result), to=sid)
    else:
        result = Result(False, "can't delete the account try again please", None)
        await sio.emit("remove_account_result", to_json(result), to=sid)


@sio.event
async def show_account(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    p = show_account_handle(player)
    if p:
        result = Result(True, "successful", p)
        await sio.emit("show_account_result", to_json(result), to=sid)
    else:
        result = Result(False, "can't show the account try again please", None)
        await sio.emit("show_account_result", to_json(result), to=sid)


async def manage_contest(contest: Contest, players: List[RemotePlayer]):
    contest.distribute()
    if contest.is_end():
        winner: Player = contest.participants[0]
        print("The Winner is: " + winner.name + " " + winner.id)
        result = Result(True, 'winner in contest', winner)
        playerrrs = load_players()
        for p in playerrrs:
            for player in players:
                await sio.emit("contest_end", "the winner is:", to_json(result),
                               to=all_player_connecting[player.id].sid)
                if p.id == player.id:
                    p.contest_id_finished.append(player.id)
                    p.currentContest.remove(contest.id)
        return

    contest.current_game = 0
    while not contest.is_round_end():
        game = contest.games[contest.current_game]
        result = Result(True, "start game", None)
        await sio.emit("notify_game_contest_start", to_json(result),
                       to=all_player_connecting[game.player1.id].sid)
        await sio.emit("notify_game_contest_start", to_json(result),
                       to=all_player_connecting[game.player2.id].sid)
        # zaher request handle
        # await start_game(game)

        win = game.get_winner()
        outcomes = [win]
        rate_player1 = calc_new_rate(game.player1.rate, [game.player2.rate], outcomes)
        rate_player2 = calc_new_rate(game.player2.rate, [game.player1.rate], inverse(outcomes))
        players = load_players()
        for p in players:
            if p.id == game.player1.id:
                p.rate = rate_player1
            if p.id == game.player2.id:
                p.rate = rate_player2
        save_players(players)

        if win == 1:
            winner = all_player_connecting[game.player1.id].sid
            loser = all_player_connecting[game.player2.id].sid
        else:
            winner = all_player_connecting[game.player2.id].sid
            loser = all_player_connecting[game.player1.id].sid
        result_loser = Result(True, "you are lose the game", None)
        result_winner = Result(True, "you are win the game", None)
        await sio.emit("game_contest_result", to_json(result_winner), to=winner)
        await sio.emit("game_contest_result", to_json(result_loser), to=loser)
        contest.current_game += 1

    contest.participants = contest.get_qualified_players()
    await manage_contest(contest, players)


async def start_contest(contest):
    remove_contest_available(contest.id)
    await manage_contest(contest, copy.deepcopy(contest.participants))


@sio.event
async def create_contest(sid, form):
    contest = create_contest_handler(form)
    if contest:
        contests = load_contest_available()
        contests.append(contest)
        save_contest_available(contests)
        # asyncio.create_task(run_at(contest.date, start_contest(contest)))
        result = Result(True, "successful", None)
        await sio.emit("create_contest_result", to_json(result), sid)
    else:
        result = Result(False, "can not create contest try again", None)
        await sio.emit("create_contest_result", to_json(result), to=sid)


@sio.event
async def join_player_to_contest(sid, data):
    _id = data['id']
    player = get_player_by_sid(sid, all_player_connecting)
    res = join_player_to_contest_handler(_id, player)
    if res:
        result = Result(True, "successful", res)
        await sio.emit("join_player_to_contest_result", to_json(result), to=sid)
    else:
        result = Result(False, "can not join you should to take due in full constraints", None)
        await sio.emit("join_player_to_contest_result", to_json(result), to=sid)


@sio.event
async def show_all_contests_available(sid):
    res = show_all_contests_available_handler()
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_all_contests_available_result", to_json(result), to=sid)
    else:
        result = Result(False, "do not exist any contest in server", None)
        await sio.emit("show_all_contests_available_result", to_json(result), to=sid)


@sio.event
async def show_my_contests_finished(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    res = show_finish_contest_handler(player)
    if res is not None:
        result = Result(True, "successful", res)
        await sio.emit("show_my_contests_finished_result", to_json(result), to=sid)
    else:
        result = Result(False, "can't show the contest finished try again please", None)
        await sio.emit("show_my_contests_finished_result", to_json(result), to=sid)


@sio.event
async def show_my_current_contests(sid):
    player = get_player_by_sid(sid, all_player_connecting)
    res = show_current_contest_handler(player)
    if res is not None:
        print(to_json(res))
        result = Result(True, "successful", res)
        await sio.emit("show_my_current_contests_result", to_json(result), to=sid)
    else:
        result = Result(False, "can't show the current contest try again please", None)
        await sio.emit("show_my_current_contests_result", to_json(result), to=sid)


@sio.event
async def save(sid, _id):
    player = get_player_by_sid(sid, all_player_connecting)
    res = save_game_handle(_id, player)
    if res:
        result = Result(True, "save is completed", None)
        await sio.emit("save_result", to_json(result), to=sid)
    else:
        result = Result(False, "can't save this game try again please", None)
        await sio.emit("save_result", to_json(result), to=sid)


@sio.event
async def show_games_saved(sid):
    print("welcom")
    player = get_player_by_sid(sid, all_player_connecting)
    #res = show_games_save_handle(player)
    res=load_games()
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("show_games_saved_result", to_json(result), to=sid)
    else:
        print("false")
        result = Result(False, "don't have any games saved", None)
        await sio.emit("show_games_saved_result", to_json(result), to=sid)


@sio.event
async def load(sid, data):
    _id = data['id']
    res = load_game_handle(_id)
    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("load_result", to_json(result), to=sid)
    else:
        result = Result(False, "n't load this game", None)
        await sio.emit("load_result", to_json(result), to=sid)


@sio.on('get_possible_moves')
async def get_possible_moves(sid, data):
    data = FirstButtonRequest.from_dict(data)
    print("fuck adnan")
    _id = data.id
    r = data.r
    c = data.c

    game = get_game_by_sid(_id, all_game_playing)
    # game.init()
    print(game.grid)
    piece = game.grid[r][c].piece

    print(piece)
    res = get_possible_moves_handle(game, piece)

    print("Start Paths")
    for path in res:
        print("\tStart Path")
        for action in path:
            print("\t\t", action)
        print("\tEnd Path")
    print("End Paths")

    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("get_possible_moves", to_json(result))
    else:
        result = Result(False, "Error", None)
        await sio.emit("get_possible_moves", to_json(result))


@sio.on('apply_action')
async def apply_action(sid, data):
    print("DATAAAA: ", data)
    data = SecondButtonRequest.from_dict(data)

    _id = data.id
    pairs = data.path

    game = get_game_by_sid(_id, all_game_playing)
    # game.init()
    print("HEEREEE: ")
    print(game.grid)

    print("PATHHHHH: ")
    for (r, c) in pairs:
        print(r, c)
    print("ENDDDD")

    path = get_path(game, pairs)

    print("Start")
    for action in path:
        print(action)
    print("end")

    print("Before: ", game.current_turn)
    res1 = apply_action_handle(game, path)
    res2 = path
    # print(res)

    print("After: ", game.current_turn)

    if res1 is not None:
        result = Result(True, 'successful', res1)
        await sio.emit("update_game", to_json(result))
        result = Result(True, 'successful', res2)
        await sio.emit("apply_path", to_json(result))
        if game.end():
            result = Result(True, "successful", game.get_the_winner())
            await sio.emit("game_over", to_json(result))
    else:
        result = Result(False, "Error", None)
        await sio.emit("update_game", to_json(result))


@sio.on('undo')
async def undo(sid, data):
    data = IdRequest.from_dict(json.loads(data))
    _id = data.id

    game = get_game_by_sid(_id, all_game_playing)

    print(game.grid)
    res = undo_handle(game)
    print(res.grid)

    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("undo", to_json(result))
    else:
        result = Result(False, "Error", None)
        await sio.emit("undo", to_json(result))


@sio.event
async def message(sid, data):
    print("sid says: ", data)
    await sio.emit("message", "fuck zaher")


@sio.on('create_new_game')
async def create_new_game(sid, data):
    player = get_player_by_sid(sid, all_player_connecting)
    game_info = GameInfo.from_dict(data)
    res = create_new_game_handle(game_info, all_game_playing, player)
    # if res is None:
    #     print("None")
    # else:
    #     print(res.grid)

    if res is not None:
        if res.player2 is not None:
            all_game_playing[res.id] = res
        else:
            all_game_waiting[res.id] = res

        result = Result(True, 'successful', res)
        await sio.emit("create_new_game", to_json(result), room=sid)
    else:
        result = Result(False, "Error", None)
        await sio.emit("create_new_game", to_json(result), room=sid)


@sio.on('initialize_game')
async def initialize_game(sid, data):
    data = IdRequest.from_dict(data)
    _id = data.id

    game = get_game_by_sid(_id, all_game_playing)

    res = initialize_game_handle(game)

    if res is not None:
        all_game_playing[res.id] = res
        result = Result(True, 'successful', res)
        await sio.emit("initialize_game", to_json(result), room=sid)
    else:
        result = Result(False, "Error", None)
        await sio.emit("initialize_game", to_json(result), room=sid)


def hint_thread_target(game):
    # from ai.alpha_beta_search import hint

    # path = hint(game)
    for _ in range(1000000000):
        pass

    print("thread exited")


#    print("ababa is here")

# asyncio.run(sio.emit("hint", to_json(path)))


@sio.event
async def hint(sid, data):
    game = get_game_by_sid(data['id'], all_game_playing)

    threading.Thread(target=hint_thread_target, args=(game,)).start()


@sio.on("join")
async def join(sid, data):
    print(data)
    # data = json.loads(data)
    # data = IdRequest.from_dict(data)
    data = JoinRequest.from_dict(data)
    # data = JoinRequest.from_dict(json.loads(data))

    id = data.id
    player = data.player

    game = get_game_by_sid(id, all_game_waiting)
    res = join_handle(game, player)

    if res is not None:
        all_game_waiting[res.id] = None
        all_game_playing[res.id] = res
        result = Result(True, 'successful', res)
        # Emit two players.
        await sio.emit("join", to_json(result))
    else:
        result = Result(False, "Error", None)
        await sio.emit("join", to_json(result))


@sio.on("all_waiting_games")
async def all_waiting_games(sid):
    games = []

    for game in all_game_waiting:
        games.append(game)

    res = WaitingGamesRequest(games)

    if res is not None:
        result = Result(True, 'successful', res)
        await sio.emit("all_waiting_games", to_json(result))
    else:
        result = Result(False, "Error", None)
        await sio.emit("all_waiting_games", to_json(result))


if __name__ == '__main__':
    web.run_app(app, host="localhost", port=8080)
