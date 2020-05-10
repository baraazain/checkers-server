from .Action import Action

class Player:

    def __init__(self,id,name,password):
        self.id=id
        self.name=name
        self.password=password
        self.rate=1000
        self.currentContest=[]

    def act(self, game) -> Action:
        pass
