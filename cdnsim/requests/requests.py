from abc import abstractmethod
from typing import Self, cast

import pandas as pd

from framework.node import LNode


class Requests:
    def __init__(self, freq: pd.Series | None):
        self._freq = freq

    @abstractmethod
    def generate(self, k: int) -> Self:
        ...

    @property
    def nrequests(self) -> int:
        return self._freq.sum() if self._freq is not None else 0

    def __radd__(self, other) -> Self:
        if other == 0:
            return self
        else:
            return self + other

    def __add__(self, other: Self) -> Self:
        return Requests(self._freq.add(other._freq, fill_value=0)) if other._freq is not None else self

    def __str__(self):
        return str(self._freq)

    def __truediv__(self, other: int) -> Self:
        assert isinstance(other, int), type(other)
        return Requests(self._freq / other if self._freq is not None else None)


class RequestMixIn(LNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._rpt = pd.Series()

    def work(self) -> None:
        while True:
            r = cast(Requests, sum(self._receive()))
            self._rpt[self.tick] = r.nrequests
            self.process_requests(r)

    @abstractmethod
    def process_requests(self, requests: Requests) -> None:
        ...
