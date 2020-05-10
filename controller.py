#from model.game import GameState, Action


#class Controller:

#    def __init__(self, game:GameState):
#        self.player1 = game.players_list[0]
#        self.player2 = game.players_list[1]
#        self.game = game
#        self.game.init()

#    def play(self):
#        while not self.game.is_terminal():
#            print(self.game.get_current_player_character(), end="\n")
#            action = self.game.get_current_player().act(self.game)
#            while not self.game.is_legal_action(action):
#                action = self.game.get_current_player().act(self.game)
#            self.game.apply_action(action)
#            self.game.print_board()
#        print(self.game.get_winner())

class A:
   def __init__(self, player1, ababa):
       self.player1 = player1
       self.ababa = ababa

class B(A):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
   
if __name__ == '__main__':
#    controller = Controller()
#    controller.play()
    b = B('ava', 'fuck')
    print(b.player1)