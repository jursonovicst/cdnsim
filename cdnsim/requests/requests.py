from typing import List, Self

import pandas as pd


#
# @pd.api.extensions.register_dataframe_accessor("requests")
# class RequestsAccessor:
#     def __init__(self, pandas_obj):
#         self._validate(pandas_obj)
#         self._obj = pandas_obj
#
#     @staticmethod
#     def _validate(obj):
#         # verify there is a column latitude and a column longitude
#         if 'content' not in obj.index.names:
#             raise AttributeError(f"Must have 'content' index, got {obj.index.names}")
#         if 'freq' not in obj.columns:
#             raise AttributeError(f"Must have 'freq', got {obj.columns}")
#
#     @property
#     def pmf(self) -> pd.Series:
#         return self._obj.freq.groupby('content').sum() / self._obj.freq.sum()
#
#     @property
#     def cdf(self) -> pd.Series:
#         return self._obj.pmf.cumsum()
#
#     def split(self, parts: int):
#         if not isinstance(parts, int) or parts < 1:
#             raise ValueError(f"Cannot divide {self.__class__.__name__} into {parts} parts")
#
#         if parts == 1:
#             return [self._obj]
#
#         return [(self._obj // parts).astype(int)] * parts
#
#     def merge(self, other: pd.DataFrame):
#         if not isinstance(other, pd.DataFrame):
#             raise ValueError(f"Cannot merge {self.__class__.__name__} into {other.__class__.__name__}")
#


class BaseSeries(pd.Series):
    @property
    def _constructor(self):
        return self.__class__

    @property
    def _constructor_expanddim(self):
        """
        Overload this if subclassed.
        """
        return BaseRequests


class BaseRequests(pd.DataFrame):
    @property
    def _constructor(self):
        return self.__class__

    @property
    def _constructor_sliced(self):
        """
        Overload this if subclassed.
        """
        return BaseSeries

    @classmethod
    def merge_requests(cls, dfs: List[Self], index) -> Self:
        if len(dfs) == 0:
            raise ValueError("Cannot merge an empty DataFrame")

        if len(dfs) == 1:
            return dfs[0]

        return dfs[0].add(cls.merge_requests(dfs[1:]), fill_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'content' not in self.index.names:
            raise SyntaxError(f"Wrong indexing {self.index.names}")
        if 'freq' not in self.columns:
            raise SyntaxError(f"Wrong column names {self.columns}")

    def split_rr(self, parts: int):
        """
        Split as round-robin
        """
        if not isinstance(parts, int) or parts < 1:
            raise ValueError(f"Cannot divide {self.__class__.__name__} into {parts} parts")

        return [self.floordiv(parts).astype(int)] * parts

#    @property
#    def center(self):
#        # return the geographic center point of this DataFrame
#        lat = self._obj.latitude
#        lon = self._obj.longitude
#        return (float(lon.mean()), float(lat.mean()))#
#
#    def plot(self):
#        # plot this array's data on a map, e.g., using Cartopy
#        pass
#
# class BaseRequests(pd.DataFrame, ABC):
#     @property
#     def _constructor(self):
#         return self.__class__
#
#     @property
#     @abstractmethod
#     def _constructor_sliced(self):
#         ...
#
#     @classmethod
#     def generate(cls, k: int) -> Self:
#         """
#         :param k: number of requests to generate
#         """
#         ...
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if 'content' not in self.index.names:
#             raise SyntaxError(f"Wrong indexing {self.index.names}")
#         if 'freq' not in self.columns:
#             raise SyntaxError(f"Wrong column names {self.columns}")
#
#     @property
#     def pmf(self) -> pd.Series:
#         return self.freq.groupby('content').sum() / self.sum()
#
#     @property
#     def cdf(self) -> pd.Series:
#         return self.pmf.cumsum()
#
#     def __radd__(self, other) -> Self:
#         if other == 0:
#             return self
#         else:
#             return self + other
#
#     def __add__(self, other: Self) -> Self:
#         """
#         Hijacking addition to define the sum of Requests objects, which is the pd.DataFrame addition of the frequencies.
#
#         The sum of
#
#         content  size
#         1        10     100
#         2        20     200
#         3        30     300
#         Name: requests, dtype: int64
#
#         and
#
#         content  size
#         3        30     1
#         4        40     2
#         5        50     3
#         Name: requests, dtype: int64
#
#         is
#
#         content  size
#         1        10     100
#         2        20     200
#         3        30     301
#         4        40     2
#         5        50     3
#         Name: requests, dtype: int64
#
#         """
#
#         if not isinstance(other, self.__class__):
#             raise ValueError(f"Cannot add {self.__class__.__name__} and {type(other)}")
#
#         if other.index.names != self.index.names:
#             raise SyntaxError(f"Index mismatch: Cannot merge indexes {self.index.names} and {other.index.names}")
#
#         return self.add(other, fill_value=0).astype(int)
#
#     def __floordiv__(self, other: int) -> List[Self]:
#         """
#         Hijacking floor division to define the division of Requests objects, which is the split of requests into *v*
#         Requests objects. Sum of frequencies may not equal!
#
#         content  size
#         1        10      10
#         2        20       2
#         3        30       6
#         Name: requests, dtype: int64
#
#         divided by 3 are three request objects
#
#         content  size
#         1        10       3
#         2        20       0
#         3        30       2
#         Name: requests, dtype: int64
#
#         content  size
#         1        10       4
#         2        20       1
#         3        30       2
#         Name: requests, dtype: int64
#
#         content  size
#         1        10       3
#         2        20       1
#         3        30       2
#         Name: requests, dtype: int64
#         """
#         if not isinstance(other, int) or other < 1:
#             raise ValueError(f"Cannot divide {self.__class__.__name__} by {type(other)}")
#
#         if other == 1:
#             return [self]
#
#         return [self.__class__(super().__floordiv__(other).astype(int))] * other
#
#     def __truediv__(self, other):
#         raise NotImplementedError("TODO: implement this, // we wil lose requests, use some randomness")
#
# # class IngressMixIn(LNode):
# #     def __init__(self, **kwargs):
# #         super().__init__(**kwargs)
# #
# #         self._ingress: List[Requests] = []
# #
# #     def _work(self) -> None:
# #         while True:
# #             r = cast(Requests, sum(self._receive()))
# #             self._ingress.append(r)
# #             self._process_ingress(r)
# #
# #     @abstractmethod
# #     def _process_ingress(self, requests: Requests) -> None:
# #         ...
# #
# #     def rpt(self) -> List[int]:
# #         return [r.nrequests for r in self._ingress]
#
# # class EgressMixIn(TNode):
# #     def __init__(self, **kwargs):
# #         super().__init__(**kwargs)
# #
# #         self._egress: List[Requests] = []
# #
# #     def process_egress(self, requests: Requests) -> None:
# #         self._egress.append(r)
