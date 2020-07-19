import datetime as dt
import json

from .actors import Player
from .grid import Cell, Grid
from .piece import Piece


def classify(rate: int) -> str:
    if rate < 1200:
        return 'novices'
    if 1200 <= rate < 1400:
        return 'Class D'
    if 1400 <= rate < 1600:
        return 'Class C'
    if 1600 <= rate < 1800:
        return 'Class B'
    if 1800 <= rate < 2000:
        return 'Class A'
    if 2000 <= rate < 2200:
        return 'Expert'
    if 2200 <= rate < 2300:
        return 'Candidate Master'
    if 2300 <= rate < 2400:
        return 'Master'
    if 2400 <= rate < 2500:
        return 'International Master'
    if rate >= 2500:
        return 'Grand Master'


def get_categories() -> list:
    return ['novices',
            'Class D',
            'Class C',
            'Class B',
            'Class A',
            'Expert',
            'Candidate Master',
            'Master',
            'International Master',
            'Grand Master']


def calc_expected_score(old_rate: int, opp_rate: int) -> float:
    res = 1 + 10 ** ((opp_rate - old_rate) / 400)
    return 1 / res


def calc_K(rate: int) -> int:
    if rate < 2100:
        return 32
    if 2200 <= rate < 2400:
        return 24
    return 16


def calc_score(player_number: int, outcome: int) -> float:
    if outcome == 0:
        return 0.5
    if outcome == player_number:
        return 1
    return 0


def inverse(arg: list) -> list:
    ret = []
    for element in arg:
        if element == 0:
            ret.append(element)
        else:
            ret.append(3 - element)
    return ret


def calc_new_rate(player_rate: int, opp_rates: list, outcomes: list) -> int:
    score = 0
    exp_score = 0


    for opp_rate, outcome in zip(opp_rates, outcomes):
        score += calc_score(1, outcome)
        exp_score += calc_expected_score(player_rate, opp_rate)

    player_rate += calc_K(player_rate) * (score - exp_score)

    return int(player_rate)


def to_dict(obj):
    if isinstance(obj, dt.datetime):
        # return dict(year=obj.year,
        #             month=obj.month,
        #             day=obj.day,
        #             hour=obj.hour,
        #             minute=obj.minute,
        #             second=obj.second,
        #             tzinfo=obj.tzinfo)
        return str(obj)
    else:
        if isinstance(obj, Grid):
            return dict(n=obj.n, m=obj.m, grid=None)
        else:
            if isinstance(obj, Piece):
                return {'color': obj.color, 'type': obj.type, 'dead': obj.dead, 'cell': to_dict(obj.cell)}
            else:
                if isinstance(obj, Cell):
                    return {'r': obj.r, 'c': obj.c, 'piece': None}
                else:
                    if isinstance(obj, Player):
                        return {'name': obj.name,
                                'password': "",
                                'id': obj.id, 'rate': obj.rate
                                }

                    return obj.__dict__


def to_json(obj):
    return json.dumps(obj, default=to_dict, indent=4)
