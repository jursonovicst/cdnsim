from abc import abstractmethod
from typing import Self
import pandas as pd

class Requests:
    def __init__(self, freq: pd.Series | None):
        self._freq = freq

    @abstractmethod
    def generate(self, k: int) -> Self:
        ...

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self + other

    def __add__(self, other: Self) -> Self:
        return Requests(self._freq.add(other._freq, fill_value=0)) if other._freq is not None else self

    def __str__(self):
        return str(self._freq)

    def __truediv__(self, other: int):
        assert isinstance(other, int), type(other)
        return Requests(self._freq / other if self._freq is not None else None)