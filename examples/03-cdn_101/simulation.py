from nodes.log import LogMixIn, LoggerMixIn

# Create the simplest CDN setup consisting of one client, one cache and a single origin.
#
# [client1] --> [cache1] --> [origin]
#
# the client requests uniform profiles according to a constant arrival processes, the caches are NonCaches, meaning,
# they do not cache at all (for demonstration purposes), and the origin just logs the number of requests received.

LoggerMixIn.setlevel(LogMixIn.INFO)

# the poisson arrival process implementation
from cdnsim.arrival import Arrival
from numpy.random import default_rng


class Poisson(Arrival):
    def __init__(self, lam: float, **kwargs):
        super().__init__(**kwargs)
        if lam <= 1:
            raise ValueError(f"lambda for poisson should be greater or equal to 1, got: {lam}")
        self.__lam = lam
        self.__rng = default_rng()

    def __next__(self) -> int:
        super().__next__()
        return int(self.__rng.poisson(self.__lam, 1)[0])


# extend the BaseRequests to track tick and content sizes
from typing import List, Hashable, Dict
import pandas as pd
from cdnsim.requests import BaseRequests


class ThroughputRequests(BaseRequests):

    def __init__(self,
                 freqs: List[int] = [],
                 index: Dict[str, List[Hashable]] = {'tick': [], 'content': [], 'size': []}):
        if 'tick' not in index.keys() or 'size' not in index.keys():
            raise SyntaxError(f"'tick', 'size' must be part of the level names, got: {index.keys()}")
        super().__init__(freqs=freqs, index=index)

    @property
    def rpt(self) -> pd.Series:
        return self.groupby('tick').sum()

    @property
    def bpt(self) -> pd.Series:
        return self.reset_index('size').prod(axis=1).groupby('tick').sum()


# the zipf client implementation
from scipy.stats import zipfian, binom

from typing import Iterator, List, Tuple

import numpy as np

from cdnsim import Client
from cdnsim.arrival import Arrival


class ZipfClient(Client):

    def __init__(self, cbase: int, n: int, p: float, a: float, arrival: Arrival):
        self._cbase = cbase
        self._csize = binom.rvs(n, p, size=cbase)
        self._a = a
        self._arrival = arrival
        super().__init__()

    def _generate(self) -> Iterator[List[Tuple[str, ThroughputRequests]]]:
        for k in self._arrival:
            r = np.unique(zipfian.rvs(self._a, self._cbase, size=k), return_counts=True)
            yield [(remote, request) for remote, request in zip(self.remotes,
                                                                ThroughputRequests(freqs=list(r[1]),
                                                                                   index={
                                                                                       'tick': np.full(self._cbase,
                                                                                                       self._arrival.tick),
                                                                                       'size': self._csize,
                                                                                       'content': list(r[0])}) // len(
                                                                    self.remotes))]


# PLFU cache implementation
from cdnsim.cache.cache import Cache


class PLFUCache(Cache):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self._size = size

    def _work(self) -> None:
        while recv := self._receive():
            requests = cast(ThroughputRequests, sum(recv))  # <-- TODO: this can be abstracted in a higher layer

            # blablabla...
            misses = requests.sort_values(ascending=False).reset_index('size').prod(axis=1).cumsum().index

            # blablabla...
            for remote, request in zip(self.remotes, request[misses] // len(self.remotes)):
                self._send(remote, request)
        self._terminate()


# origin implementation
from typing import cast

from cdnsim.requests import BaseRequests
from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._requests = BaseRequests([], {'tick': [], 'content': []})

    def _work(self) -> None:
        while recv := self._receive():
            assert isinstance(recv, list) and len(recv) > 0, recv
            self._log(f"received {cast(BaseRequests, sum(recv)).sum()} requests")


if __name__ == "__main__":

    # create client
    client1 = ZipfClient(cbase=20, n=50, p=0.5, a=1.6, arrival=Poisson(lam=50, ticks=10))
    client2 = ZipfClient(cbase=100, n=200, p=0.3, a=1.1, arrival=Poisson(lam=80, ticks=10))

    # create caches
    cache1 = PLFUCache(size=10)
    cache2 = PLFUCache(size=10)
    cache3 = PLFUCache(size=20)

    # create origin
    origin = Origin()

    # establish connections
    client1.connect_to(cache1)
    client1.connect_to(cache2)
    client2.connect_to(cache1)
    client2.connect_to(cache2)
    cache1.connect_to(cache3)
    cache2.connect_to(cache3)
    cache3.connect_to(origin)

    # run simulation
    try:
        client1.start_all()
        client1.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        client1.terminate_all()
