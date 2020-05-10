class Action:
    
    def __init__(self,source,distination,player):
        self.id=-1
        self.source=sorce
        self.distination=distination
        self.player=player
        self.eat=None

    def __str__(self):
        ret = "("+self.getSource.getR+1 +","+self.getSource.getC+1 +")"
        ret += "------->>>"
        ret += "("+self.distination+1 +","+self.distination.getC+1 +")"

    def __eq__(self,other):
        return isinstance(other,Action) and self.source==other.source and self.distination==other.distination and self.id==other.id

   
