import pandas as pd

from cdnsim.requests import BaseRequests
from nodes.log import LogMixIn, LoggerMixIn

# Create the simplest CDN setup consisting of one client, one cache and a single origin.
#
# [client1] --> [cache1] --> [origin]
#
# the client requests uniform profiles according to a constant arrival processes, the caches are NonCaches, meaning,
# they do not cache at all (for demonstration purposes), and the origin just logs the number of requests received.

LoggerMixIn.setlevel(LogMixIn.INFO)

# the constant arrival process
from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrivals in every tick.
    """

    def __init__(self, rate: float, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate

    def __next__(self) -> int:
        super().__next__()
        return int(self.__rate)


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
#     def split(self, parts: int) ->  list[pd.DataFrame]:
#         if not isinstance(parts, int) or parts < 1:
#             raise ValueError(f"Cannot divide {self.__class__.__name__} into {parts} parts")
#
#         if parts == 1:
#             return [self._obj]
#         return [(self._obj // parts).astype(int)] * parts
#
#     @staticmethod
#     def merge(dfs: list[pd.DataFrame]):
#         if not isinstance(other, pd.DataFrame):
#             raise ValueError(f"Cannot merge {self.__class__.__name__} into {other.__class__.__name__}")
#


# the uniform client implementation
import numpy as np
from scipy.stats import randint

from cdnsim import Client
from cdnsim.arrival import Arrival


class Uniform(Client):
    """
    Uniform client, *cbase* number of contents, each content is requested with the same probability.
    """

    def __init__(self, cbase: int, arrival: Arrival, **kwargs):
        self._cbase = cbase
        self._arrival = arrival
        super().__init__(**kwargs)

    def _work(self, *args) -> None:
        for k in self._arrival:
            r = np.unique(randint.rvs(1, self._cbase + 1, size=k), return_counts=True)
            self._send(
                BaseRequests(data={'freq': r[1]}, index=pd.MultiIndex.from_arrays([r[0]], names=['content'])).split(
                    len(self.remotes)))


# noncache implementation
from cdnsim.cache import Cache


class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """

    def _work(self) -> None:
        # receive messages from all remotes until termination (empty list) received
        while (msgs := self._receive()) is not None:
            requests = BaseRequests.merge(msgs)
            # in-->out (no caching)
            self._send(requests.split(len(self.remotes)))


# origin implementation

from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode):
    """
    Simple origin implementation. Logs the number of requests received.
    """

    def _work(self) -> None:
        # receive messages from all remotes until termination (empty list) received
        while (msgs := self._receive()) is not None:
            # merge incoming requests
            requests = BaseRequests.merge(msgs)

            # log number of requests received
            self._log(f"received {requests.freq.sum()} requests")


if __name__ == "__main__":

    # create nodes
    client = Uniform(cbase=20, arrival=Constant(rate=50, ticks=5))
    cache = NonCache()
    origin = Origin()

    # establish connections
    client.connect_to(cache)
    cache.connect_to(origin)

    # run simulation
    try:
        Client.start_all()
        Client.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        Client.terminate_all()
