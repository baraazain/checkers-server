class Result:

    def __init__(self, state, message, _object):
        self.state = state
        self.message = message
        self.object = _object

    @classmethod
    def from_dict(cls, dictionary):
        r = cls(None, None, None)
        r.__dict__ = dictionary
        return r
