class Result:

    def __init__(self, state, message, _object,type):
        self.state = state
        self.message = message
        self.object = _object
        self.type=type

    @classmethod
    def from_dict(cls, dictionary):
        r = cls(None, None, None)
        r.__dict__ = dictionary
        return r
