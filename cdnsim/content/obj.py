from typing import Hashable


class Obj(object):
    """
    Represents an object by its hash value.
    """

    def __init__(self, datahash: int | Hashable):
        """
        :param datahash: hash value of the object (if it is a non-integer type, will be hashed)
        """
        self.__hash = datahash if isinstance(datahash, int) else hash(datahash)

    def __repr__(self):
        return f"<Obj {self.__hash} at {hex(id(self))}>"

    def __str__(self):
        return str(self.__hash)
