import asyncio
import datetime

from .helper import *
from model.contest import Contest
import json


def create_contest_handler(form):
    form = form.from_dict(json.loads(form))
    contests = load_contest()
    if len(contests) == 0:
        new_id = 1
    else:
        new_id = contests[len(contests) - 1].id + 1
    for con in contests:
        if form.name == con.name:
            return None
    contest = Contest(new_id, form.name, form.date, form.mode)
    contests.append(contest)
    save_contest(contests)
    return contest


def join_player_to_contest_handler(_id, player):
    contests: list = load_contest()
    res = None
    for contest in contests:
        if contest.id == _id:
            res = contest.add_new_player(player)
    players = load_players()
    for p in players:
        if p.id == player.id:
            p.currentContest.append(_id)
    save_contest(contests)
    return res


def show_finish_contest_handler(playerx):
    players: list = load_players()
    contests: list = []
    for player in players:
        if player.id == playerx.id:
            for _id in player.contest_id_finished:
                contests.append(get_contest_by_id(_id))

            return contests
    return None


def show_current_contest_handler(playerx):
    players: list = load_players()
    contests: list = []
    for player in players:
        if player.id == playerx.id:
            for _id in player.currentContest:
                contests.append(get_contest_by_id(_id))

            return contests
    return None


async def wait_for(date):
    # sleep until the specified datetime
    while True:
        now = datetime.datetime.now()
        remaining = (date - now).total_seconds()
        if remaining < 86400:
            break
        # asyncio.sleep doesn't like long sleeps, so don't sleep more
        # than a day at a time
        await asyncio.sleep(86400)
    await asyncio.sleep(remaining)


async def run_at(date, emit):
    await wait_for(date)
    return await emit
