class Cell:


   def __init__(self, row, col,piece):
       self.r=row
       self.c=col
       self.piece=piece

   def setContent(self,content):
       self.piece.setContent(content)
  
   def setType(self,type):
       self.piece.setType(type)

   def getType(self):
       return self.piece.getType()

   def getContent(self):
       if self.piece is None:
           return None
       return self.piece.getContent()

   def __str__(self):
       return "("+self.r+1 +","+self.c+1 +")"

   def __eq__(self,other):
       return isinstance(other,Cell) and self.r==other.r and self.c==other.c and self.piece==other.piece
