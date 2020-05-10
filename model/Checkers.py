import Game
import InternationalGame
import DateYMD
import RandomBotPlayer
class Checkers:
    def __init__(self):
        self.games=[]
        self.players=[]
        self.contests=[]



    def startNewGame (player1,player2):
         game =InternationalGame(1, player1, player2,DateYMD(4, 3, 2020))
         game.init()
         while not game.end():
            game.playTurn()
            game.grid.print()
            game.printTheWinner()
   
            

    def startNewContest(self,name,  date, playerss, constraints):
         contest =Contest(1, name, date, Mode.INTERNATIONAL);
         contest.addConstraints(constraints);
         for i in self.playerss:
           contest.addNewPlayer(i);
           contest.manage();
    

def main():
    checker=Checkers()
    player1 = RandomBotPlayer(3, "Ababa", "Ababa Password :)")
    player2 = RandomBotPlayer(4, "Ababa", "Ababa Password :)")
    checker.players.append(player1)
    checker.players.append(player2)
    checker.startNewGame(player1,player2)








if __name__=="__main__":main()
