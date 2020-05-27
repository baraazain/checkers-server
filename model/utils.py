import datetime as dt
import json

from .grid import Grid, Cell
from .piece import Piece
from .actors import Player


def to_dict(obj):
    # as datetime class has no __dict__ attribute
    # I dont know why!!
    if isinstance(obj, dt.datetime):
        return dict(year=obj.year, 
                    month=obj.month, 
                    day=obj.day, 
                    hour=obj.hour, 
                    minute=obj.minute, 
                    second=obj.second, 
                    tzinfo = obj.tzinfo)

    else:
        if isinstance(obj, Grid):
            return dict(n=obj.n, m=obj.m, grid=None)
        else:
            if isinstance(obj, Piece):
                return {'color': obj.color, 'type':obj.type, 'dead': obj.dead, 'cell': to_dict(obj.cell)}
            else:
                if isinstance(obj, Cell):
                    return {'r': obj.r, 'c':obj.c, 'piece':None}
                else:
                    return obj.__dict__

def to_json(obj):
    return json.dumps(obj, default=to_dict, indent=4)

