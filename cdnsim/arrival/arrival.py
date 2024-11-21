from abc import ABC, abstractmethod


class Arrival(ABC):

    def __init__(self, ticks: int, **kwargs):
        super().__init__(**kwargs)
        self.__ticks = ticks

    def __iter__(self):
        self._tick = self.__ticks
        return self

    @abstractmethod
    def __next__(self) -> int:
        ...
