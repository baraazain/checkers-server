import Player
import random
class BotPlayer(Player):

    def __init__(self,id,name,password):
        super.__init__(id,name,password)
   
    def makeMove(game):
        print("size:"+len(game.getWhitePieces()))

        for i in game.getWhitePieces():
            i.print()

        print("\n")
        print(game.grid.print())

        moves=game.getAllPossibleMoves()
        result=random.choice(moves)
        return moves[result]