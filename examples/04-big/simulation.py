from nodes.log import LogMixIn, LoggerMixIn

# Create a big CDN setup consisting of three tiers
#
# first tier:  24 pops, 30 servers each pop
# second tier: 24 pops, 4 servers each pop
# third tier: 1 pop, 30 servers
#
# the clients are requesting different profiles of Zipf distribution according to different arrival processes, the
# caches are NonCaches, meaning, they do not cache at all (just for this example), and the origin is a simple origin.

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

    def __init__(self, cbase: int, n: int, p: float, a: float, arrival: Arrival, **kwargs):
        self._cbase = cbase
        self._csize = binom.rvs(n, p, size=cbase)
        self._a = a
        self._arrival = arrival
        super().__init__(**kwargs)

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


    origin = Origin()

    l3caches=[]
    for server in range(30):
        c = PLFUCache(name=f"cache_l3_no{server}", size=100)
        c.connect_to(origin)
        l3caches.append(c)

    pops=[]
    for pop in range(24):
        l2caches=[]
        for server in range(4):
            c = PLFUCache(name=f"cache_l2_pop{pop}_no{server}", size=20)
            for l3 in l3caches:
                c.connect_to(l3)
            l2caches.append(c)

        l1caches=[]
        for server in range(24):
            c = PLFUCache(name=f"cache_l1_pop{pop}_no{server}", size=5)
            for l2 in l2caches:
                c.connect_to(l2)
            l1caches.append(c)

        client = ZipfClient(name=f"client_pop{pop}", cbase=1000, n=200, p=0.3, a=1.1, arrival=Poisson(lam=300, ticks=3600))
        for c in l1caches:
            client.connect_to(c)
        pops.append([*l2caches, l1caches, client])

    # run simulation
    try:
        ZipfClient.start_all()
        ZipfClient.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        ZipfClient.terminate_all()
