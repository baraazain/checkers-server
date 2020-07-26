class Message:
    def __init__(self, text, sender):
        self.text = text
        self.sender = sender

    @classmethod
    def from_dict(cls, data):
        return Message(**data)

