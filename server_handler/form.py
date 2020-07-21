import datetime as dt


class Form:
    def __init__(self, name, date, mode, rate, count_of_player):
        self.name = name
        self.date = dt.datetime.fromisoformat(date)
        self.mode = mode
        self.rate = rate
        self.count_of_player = count_of_player

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)
