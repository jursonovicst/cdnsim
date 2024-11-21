from abc import abstractmethod
from typing import Self, cast, List

import pandas as pd

from nodes.node import LNode


class Requests:
    def __init__(self, freq: pd.Series | None):
        if freq is not None:
            assert freq.index.nlevels == 2 and \
                   freq.index.names == ['content', 'size'] and \
                   freq.dtype == 'int64', f"wrong index, got {freq}"
        self._freq = freq
        if freq is not None:
            self._freq.name = 'requests'

    @abstractmethod
    def generate(self, k: int) -> Self:
        """
        :param k: number of requests to generate
        """
        ...

    @property
    def nrequests(self) -> int:
        """
        Sum of individual requests
        """
        return self._freq.sum() if self._freq is not None else 0

    @property
    def bytes(self) -> int:
        """
        Sum of bytes requested
        """
        return self._freq.reset_index('size').prod(axis=1).sum() if self._freq is not None else 0

    def __radd__(self, other) -> Self:
        if other == 0:
            return self
        else:
            return self + other

    def __add__(self, other: Self) -> Self:
        """
        Defines the addition of two Requests objects, which is the pd.Series addition of the two frequencies.

        The sum of

        content  size
        1        10     100
        2        20     200
        3        30     300
        Name: requests, dtype: int64

        and

        content  size
        3        30     1
        4        40     2
        5        50     3
        Name: requests, dtype: int64

        is

        """
        return Requests(self._freq.add(other._freq, fill_value=0).astype(int)) if other._freq is not None else self

    def __str__(self):
        return str(self._freq)

    def __truediv__(self, v: int) -> List[Self]:
        """
        Defines the division of two Requests objects, which means a split of requests into *v* Requests objects, but
        keeping the sum of request numbers.

        content  size
        1        10      10
        2        20       2
        3        30       6
        Name: requests, dtype: int64

        divided by 3 are three request objects

        content  size
        1        10       3
        2        20       0
        3        30       2
        Name: requests, dtype: int64

        content  size
        1        10       4
        2        20       1
        3        30       2
        Name: requests, dtype: int64

        content  size
        1        10       3
        2        20       1
        3        30       2
        Name: requests, dtype: int64
        """
        if not isinstance(v, int):
            raise SyntaxError(f"Cannot divide {self.__class__.__name__} by {type(v)}")

        # TODO: fix this, cannot provide non integer frequency numbers. Use some randomness.
        return [Requests((self._freq / v).astype(int) if self._freq is not None else None) for i in range(v)]


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
