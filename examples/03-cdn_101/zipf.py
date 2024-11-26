import numpy as np
import pandas as pd
from scipy.stats import zipfian, binom

from cdnsim import Client
from cdnsim.arrival import Arrival
from throughput import ThroughputRequests


class ZipfClient(Client):

    def __init__(self, cbase: int, n: int, p: float, a: float, arrival: Arrival, **kwargs):
        self._cbase = cbase
        self._csize = binom.rvs(n, p, size=cbase)
        self._a = a
        self._arrival = arrival
        super().__init__(**kwargs)

    def _work(self, *args) -> None:
        for k in self._arrival:
            r = np.unique(zipfian.rvs(self._a, self._cbase, size=k), return_counts=True)
            ticks = np.full(len(r[0]), self._arrival.tick)
            sizes = np.take(self._csize, r[0] - 1)

            assert len(ticks) == len(sizes) == len(r[0]), f"{ticks}, {sizes}, {r[0]}"

            index = pd.MultiIndex.from_arrays([ticks, r[0]], names=['tick', 'content'])
            self._send(ThroughputRequests(data={'freq': r[1], 'size': sizes}, index=index).split_rr(len(self.remotes)))
