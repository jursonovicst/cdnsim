from abc import abstractmethod
from typing import List, Hashable
from typing import Self, Dict

import pandas as pd


class Requests(pd.Series):

    @classmethod
    @abstractmethod
    def generate(cls, k: int) -> Self:
        """
        :param k: number of requests to generate
        """
        ...

    def __init__(self, freqs: List[int] = [], index: Dict[str, List[Hashable]] = {'content': []}):

        if 'content' not in index.keys():
            raise SyntaxError(f"'content' must be part of the level names, got: {index.keys()}")
        super().__init__(data=freqs, name='request',
                         index=pd.MultiIndex.from_arrays(list(index.values()), names=index.keys()))

    @property
    def nrequests(self) -> int:
        """
        Sum of individual requests
        """
        return 0 if self.empty else self.sum()

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
        return 0 if self.empty else self.add(other, fill_value=0).astype(int)

    def __floordiv__(self, other: int) -> List[Self]:
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
        if not isinstance(other, int) or other < 1:
            raise SyntaxError(f"Cannot divide {self.__class__.__name__} by {type(other)}")

        if other == 1:
            return [self]

        d = super().__floordiv__(other).astype(int)
        assert isinstance(d, pd.Series), d

        return [Requests(freqs=d.values,
                         index={name: values for name, values in zip(self.index.names, self.index.levels)})] * other

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
