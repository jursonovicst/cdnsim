from typing import Iterator, List, Tuple

import numpy as np
from scipy.stats import randint

from cdnsim import Client
from cdnsim.arrival import Arrival
from cdnsim.requests import Requests


class Uniform(Client):
    def __init__(self, cbase: int, arrival: Arrival):
        self._cbase = cbase
        self._arrival = arrival
        super().__init__()

    def _generate(self) -> Iterator[List[Tuple[str, Requests]]]:
        for k in self._arrival:
            r = np.unique(randint.rvs(1, self._cbase + 1, size=k), return_counts=True)
            yield [(remote, request) for remote, request in
                   zip(self.remotes, Requests(freqs=list(r[1]), index={'content': list(r[0])}) // len(self.remotes))]
