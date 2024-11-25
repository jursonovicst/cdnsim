from abc import ABC
from typing import List
from typing import Self

import pandas as pd


class BaseRequests(pd.Series, ABC):

    @classmethod
    def generate(cls, k: int) -> Self:
        """
        :param k: number of requests to generate
        """
        ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'content' not in self.index.names:
            raise SyntaxError(f"No content {self.index.names}")

    @property
    def pmf(self) -> pd.Series:
        return self.groupby('content').sum() / self.sum()

    @property
    def cdf(self) -> pd.Series:

        return self.pmf.cumsum()

    def __radd__(self, other) -> Self:
        if other == 0:
            return self
        else:
            return self + other

    def __add__(self, other: Self) -> Self:
        """
        Hijacking addition to define the sum of Requests objects, which is the pd.Series addition of the frequencies.

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

        content  size
        1        10     100
        2        20     200
        3        30     301
        4        40     2
        5        50     3
        Name: requests, dtype: int64

        """

        if not isinstance(other, self.__class__):
            raise ValueError(f"Cannot add {self.__class__.__name__} and {type(other)}")

        if other.index.names != self.index.names:
            raise SyntaxError(f"Index mismatch: Cannot merge indexes {self.index.names} and {other.index.names}")

        return self.add(other, fill_value=0).astype(int)

    def __floordiv__(self, other: int) -> List[Self]:
        """
        Hijacking floor division to define the division of Requests objects, which is the split of requests into *v*
        Requests objects. Sum of frequencies may not equal!

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
        if not isinstance(other, int) or other < 1:
            raise ValueError(f"Cannot divide {self.__class__.__name__} by {type(other)}")

        if other == 1:
            return [self]

        return [self.__class__(super().__floordiv__(other).astype(int))] * other

    def __truediv__(self, other):
        raise NotImplementedError("TODO: implement this, // we wil lose requests, use some randomness")

# class IngressMixIn(LNode):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self._ingress: List[Requests] = []
#
#     def _work(self) -> None:
#         while True:
#             r = cast(Requests, sum(self._receive()))
#             self._ingress.append(r)
#             self._process_ingress(r)
#
#     @abstractmethod
#     def _process_ingress(self, requests: Requests) -> None:
#         ...
#
#     def rpt(self) -> List[int]:
#         return [r.nrequests for r in self._ingress]

# class EgressMixIn(TNode):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self._egress: List[Requests] = []
#
#     def process_egress(self, requests: Requests) -> None:
#         self._egress.append(r)
