import datetime as dt


class Form:
    def __init__(self, name, date, mode, min_rate, max_rate, count_of_player):
        self.name = name
        self.date = dt.datetime.fromisoformat(date)
        self.mode = mode
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.count_of_player = count_of_player

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)
