from abc import ABC, abstractmethod


class Arrival(ABC):
    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __next__(self) -> int:
        ...
