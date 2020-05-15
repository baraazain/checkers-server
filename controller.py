from model.InternationalGame import InternationalGame
from model.Actors import RandomAgent
import datetime as dt


class A:
   @classmethod
   def build(cls, ababa):
       return cls(None, ababa)

   def get(self):
       return self.ababa

   def __init__(self, player1, ababa):
       self.player1 = player1
       self.ababa = ababa


class B(A):
    @classmethod
    def build(cls, ababa):
        return cls(None, ababa - 1)

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class en:
    def __init__(self, a):
        self.cls = a.__class__
    def get(self):
        a: A = self.cls.build(12)
        return a.get()


def main():
    game = InternationalGame(1, RandomAgent(), RandomAgent(), dt.datetime.now())
    game.init()
    print(game.grid)
    while not game.end():
        print(game.currentTurn, end="\n")
        action = game.getCurrentPlayer().act(game)
        while not game.isLegalAction(action):
            action = game.getCurrentPlayer().act(game)
        game.applyAction(action)
        print(game.grid)
    game.printTheWinner()

if __name__ == '__main__':
    #main()
    pass
