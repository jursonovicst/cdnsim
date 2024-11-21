from abc import ABC


class Arrival(ABC):
    """
    An abstract class to provide the general interfaces for an arrival process implementation. By itself is an iterator.

    Tracks time with the tick property.
    """

    def __init__(self, ticks: int, **kwargs):
        super().__init__(**kwargs)
        self.__ticks = ticks

    def __iter__(self):
        # initialize
        self.__tick = -1
        return self

    def __next__(self) -> int | None:
        self.__tick += 1
        if self.__tick >= self.__ticks:
            del self.__tick
            raise StopIteration
        return None

    @property
    def tick(self) -> int:
        """
        returns the tick of the interator. Defined only during iteration.
        """
        return self.__tick
