from copy import deepcopy
class A:
    def __init__(self):
        self.a = 'fuck'
    def from_object_to_dict(self):
        return self.__dict__
    @classmethod
    def from_dict_to_object(cls, dictonary, copy=True):
        if copy:
            dictonary = deepcopy(dictonary)
        a = A()
        #override attributes it will work only if all of them are simple object
        a.__dict__ = dictonary
        return a;
    def __str__(self):
        return self.a
class B:
    def __init__(self):
        self.a = A()
        self.b = 'you'
    def from_object_to_dict(self):
        return {'a': self.a.from_object_to_dict(),
                'b': self.b}
    @classmethod
    def from_dict_to_object(cls, dictonary, copy=True):
        if copy:
            dictonary = deepcopy(dictonary)
        # need to convert Object attributes from json format to python Objects
        dictonary['a'] = A.from_dict_to_object(dictonary['a'], copy = False)
        b = B()
        # because all the other attributes is now simple or python objects this will work to override attributes
        b.__dict__ = dictonary
        return b
    def __str__(self):
        return str(self.a) + self.b
import json
if __name__ == '__main__':
    # main()
    b = B()
    map = b.to_dict()
    jsonstring = json.dumps(map, indent=4)
    print(jsonstring)
    map = json.loads(jsonstring)
    b = B.from_dict(map)
    print(b)