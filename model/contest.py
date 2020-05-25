import datetime
from copy import deepcopy
from .actors import Player
from .game import Mode
from .international_game import InternationalGame


class Constraint:
    """An abstract interface"""

    def is_valid(self, player: Player) -> bool:
        pass


class MaxParticipantsConstraint(Constraint):
    def __init__(self, max_participant, num_of_participants):
        self.max_participant = max_participant
        self.num_of_participants = num_of_participants

    def is_valid(self, player):
        return self.num_of_participants + 1 <= self.max_participant


class NameConstraint(Constraint):
    def __init__(self):
        self.names = []

    def is_valid(self, player: Player):
        for name in self.names:
            if player.name == name:
                return True
        return False


class RatingConstraint(Constraint):
    def __init__(self, mn=-1e9, mx=1e9):
        self.min = mn
        self.max = mx

    def is_valid(self, player: Player):
        return self.min <= player.rate <= self.max


class DateConstraint(Constraint):
    def __init__(self, date: datetime.date):
        self.date = date

    def is_valid(self, player):
        return datetime.date.today() <= self.date


class Contest:
    def __init__(self, _id, name, date: datetime.datetime, mode: Mode):
        self.id = _id
        self.name = name
        self.date = date
        self.mode = mode
        self.last_game_id = 1
        self.games = []
        self.constraints = []
        self.participants = []
        self.current_game = 0

    # bug current game is an object
    # bug date is an object 
    # note: 
    #       datetime object in python dont have a __dict__ member and I dont know why!!
    # bug participants is list of objects
    # bug game is list of objects
    # consider using the other bug free method e.g json.dumps(obj, defualt = utils.to_dict)
    def from_object_to_dict(self):
       return {'id':self.id,'name':self.name,'date':self.date,'mode':self.mode,'last_game_id':self.last_game_id,'games':self.games,'constraints':self.constraints,'participants':self.participants,'current_game':self.current_game}

   # your forgetting to put cls argument
   # in python the first argument to class methods must be cls
    @classmethod
    def from_dict_to_object(dictionary):
        # it turns out this method is wrong 
        # dont copy the dictioary
        # convert every member to an indivual object then use the constructor of the class
        # without modifiying the dictionary it self
        # like this  object = objectclass.from_dict_to_object(dictionary['object'])
        # object2 = ... and so on
        # then use the constructor for this class
        dictionary=deepcopy(dictionary)
        # bug there is no constructor with zero arguments for class Contest
        c=Contest()
        c.__dict__=dictionary
        return c
    def add_new_player(self, player: Player) -> None:
        for constraint in self.constraints:
            if not constraint.is_valid(player):
                return
        self.participants.append(player)

    def distribute(self):
        self.games.clear()
        for i in range(1, len(self.participants), 2):
            maximizer = self.participants[i - 1]
            minimizer = self.participants[i]

            coming_date = self.date
            self.date += datetime.timedelta(days=i - 1)

            if self.mode == Mode.INTERNATIONAL:
                self.games.append(InternationalGame(self.last_game_id + 1, maximizer, minimizer, coming_date))

    def get_qualified_players(self):
        qualified_participants = []
        for game in self.games:
            winner = game.get_winner()
            if winner is None:
                pass
            else:
                qualified_participants.append(winner)
        return qualified_participants

    def is_round_end(self):
        return self.current_game <= len(self.games)

    def is_end(self):
        return len(self.participants) <= 1

    def mange(self):
        self.distribute()
        if self.is_end():
            winner: Player = self.participants[0]
            print("The Winner is: " + winner.name + " " + winner.id)
            return

        self.current_game = 0
        while not self.is_round_end():
            game = self.games[self.current_game]
            self.current_game += 1
            # control the game
        self.participants = self.get_qualified_players()
        self.mange()

    def add_constraints(self, constraints):
        self.constraints.extend(constraints)
