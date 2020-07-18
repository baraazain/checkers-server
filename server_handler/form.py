class form:
    def __init__(self, name, date, mode, constraints):
        self.name = name
        self.date = date
        self.mode = mode
        self.constraints = constraints

    @classmethod
    def from_dict(cls, dictionary):

        return cls(dictionary['name'], dictionary["date"], dictionary["mode"], dictionary["mode"])
