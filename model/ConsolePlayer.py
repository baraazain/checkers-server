from .Player import *

class ConsolePlayer(Player):

    def __init__(self, id, name,password):
        super.__init__(id, name, password)

    def act(self, game):
        actions = game.get_all_possible_actions()
        size = len(action)
        for idx, action in enumerate(actions):
            print(str(idx + 1) + "." + str(action))
        while True:
            choice = int(input('Enter your choice:'))
            if 0 > choice or size < choice:
                continue
            return actions[choice - 1]


