class IdRequest:
    def __init__(self, id):
        self.id = id

    @classmethod
    def from_dict(cls, data):
        return IdRequest(**data)


class FirstButtonRequest:
    def __init__(self, id, r, c):
        self.id = id
        self.r = r
        self.c = c

    @classmethod
    def from_dict(cls, data):
        return FirstButtonRequest(**data)


class SecondButtonRequest:
    def __init__(self, id, path):
        self.id = id
        self.path = path

    @classmethod
    def from_dict(cls, data):
        return SecondButtonRequest(**data)


class JoinRequest:
    def __init__(self, id, player):
        self.id = id
        self.player = player

    @classmethod
    def from_dict(cls, data):
        return JoinRequest(**data)


class WaitingGamesRequest:
    def __init__(self, games):
        self.games = games

    @classmethod
    def from_dict(cls, data):
        return WaitingGamesRequest(**data)
