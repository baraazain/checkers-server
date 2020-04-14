from model.game import GameState
import datetime
import json as js

class Controller:

    def __init__(self, game:GameState):
        self.player1 = game.players_list[0]
        self.player2 = game.players_list[1]
        self.game = game
        self.game.init()

    def play(self):
        while not self.game.is_terminal():
            print(self.game.get_current_player_character(), end="\n")
            action = self.game.get_current_player().act(self.game)
            while not self.game.is_legal_action(action):
                action = self.game.get_current_player().act(self.game)
            self.game.apply_action(action)
            self.game.print_board()
        print(self.game.get_winner())


if __name__ == '__main__':
#    controller = Controller()
#    controller.play()
    print(10)
    js.decoder.JSONDecoder()