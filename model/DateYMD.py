import datetime
class DateYMD:

    def __init__(self,day,month,yeaar):
        self.day=day 
        self.month=month
        self.year=year


    def setDay(self,day):
        self.day=day

    def getDay(self):
        return self.day

    def setMonth(self,month):
        self.month=month

    def getMonth(self):
       return self.month

    def setYear(self,year):
       self.year=year

    def getYear(self):
        return self.year

    ############### i dont know what zaher is meaning in function add day i write get date update this function##########
    def getCurrentDate():
        t=datetime.datetime.now()
        day=t.day
        month=t.month
        year=t.year
        date=DateYMD(day,month,year)
        return date

    def __eq__(self,other):
        return instance(other,DateYMD) and self.day==other.day and self.month==other.month and self.year==other.year

    def __cmp__(self,other):
        if self.year < other.year:return -1
        elif self.year > other.year:return 1           
        elif self.month <other.month:return -1
        elif self.month >other.month:return 1
        elif self.day <other.day:return -1
        elif self.day>other.day:return 1
        else:return 0

