from abc import ABC, abstractmethod

class Arrival(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> int:
        ...