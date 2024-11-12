from abc import abstractmethod
from typing import Self, cast, List

import pandas as pd

from nodes.node import LNode


class Requests:
    def __init__(self, freq: pd.Series | None):
        if freq is not None:
            assert len(freq.index.shape) == 1, f"frequency index must have a single level shape, got {freq.index.shape}"
            assert freq.index.dtype == 'int64', f"frequency index must have dtype int64, got {freq.index.dtype}"
            assert freq.dtype == 'int64', f"frequency values must have dtype int64, got {freq.dtype}"
        self._freq = freq

    @abstractmethod
    def generate(self, k: int) -> Self:
        """
        :param k: number of requests to generate
        """
        ...

    @property
    def nrequests(self) -> int:
        """
        Number of individual requests
        """
        return self._freq.sum() if self._freq is not None else 0

    def __radd__(self, other) -> Self:
        if other == 0:
            return self
        else:
            return self + other

    def __add__(self, other: Self) -> Self:
        """
        Defines the addition of two Requests objects, which is the pd.Series addition of the two frequencies.

        The sum of

        frequency:  10,20,30
        index:       1, 2, 3

        and

        frequency:   1, 2, 3
        index:       3, 4, 5

        is

        frequency:  10,20,31, 2, 3
        index:       1, 2, 3, 4, 5

        """
        return Requests(self._freq.add(other._freq, fill_value=0)) if other._freq is not None else self

    def __str__(self):
        return str(self._freq)

    def __truediv__(self, v: int) -> List[Self]:
        """
        Defines the division of two Requests objects, which means a split of requests into *v* Requests objects, but
        keeping the sum of request numbers.

        frequency:  10, 2, 6
        index:       1, 2, 3

        divided by 3 are three request objects

        frequency:   3, 0, 2     4, 1, 2     3, 1, 2
        index:       1, 2, 3     1, 2, 3     1, 2, 3
        """
        if not isinstance(v, int):
            raise SyntaxError(f"Cannot divide {self.__class__.__name__} by {type(v)}")

        # TODO: fix this, cannot provide non integer frequency numbers. Use some randomness.
        return [Requests(self._freq / v if self._freq is not None else None) for i in range(v)]


class IngressMixIn(LNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._ingress: List[Requests] = []

    def _work(self) -> None:
        while True:
            r = cast(Requests, sum(self._receive()))
            self._ingress.append(r)
            self._process_ingress(r)

    @abstractmethod
    def _process_ingress(self, requests: Requests) -> None:
        ...

    def rpt(self) -> List[int]:
        return [r.nrequests for r in self._ingress]

# class EgressMixIn(TNode):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self._egress: List[Requests] = []
#
#     def process_egress(self, requests: Requests) -> None:
#         self._egress.append(r)
