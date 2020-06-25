from abc import ABC, abstractmethod

from .action import Action


class Player(ABC):

    def __init__(self, _id, name, password):
        self.id = _id
        self.name = name
        self.password = password
        self.rate = 1000
        self.currentContest = []

    @abstractmethod
    def act(self, game) -> Action:
        pass

    def __eq__(self, other):
        if isinstance(other, Player):
            if other is self:
                return True
            if self.id == other.id:
                return True
        return False

    def on_update(self, action):
        pass

    def on_start(self, game):
        pass

    def __str__(self):
        return ''.join([str(self.id), ' ', self.name, ' ', self.password])


class Human(Player, ABC):
    pass


class ConsolePlayer(Human):
    def __init__(self, _id, name, password):
        super().__init__(_id, name, password)

    def act(self, game):
        paths = game.get_all_possible_actions()
        size = len(paths)

        for idx, path in enumerate(paths):
            print(''.join([str(idx + 1),
                           ". ",
                           ''.join(list(map(str, path)))
                           ])
                  )

        while True:
            choice = int(input('Enter your choice:'))
            if 0 > choice or size < choice:
                continue
            return paths[choice - 1]


class RemotePlayer(Human):
    def __init__(self, sid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sid = sid

    @classmethod
    def from_dict(cls, data):
        return cls(None, data['id'], data['name'], data['password'])

    def act(self, game):
        pass


class Agent(Player, ABC):
    pass
