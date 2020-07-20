class form:
    def __init__(self, name, date, mode):
        self.name = name
        self.date = date
        self.mode = mode

    @classmethod
    def from_dict(cls, dictionary):
        return cls(dictionary['name'], dictionary["date"], dictionary["mode"])
