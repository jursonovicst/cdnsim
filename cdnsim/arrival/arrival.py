from abc import ABC, abstractmethod
from typing import Iterator


class ArrivalMixIn(ABC):
    @abstractmethod
    def _arrival(self) -> Iterator[int]:
        """
        Implement it to draw non-negative integers.
        :return: iterator of integers.
        """
        ...
