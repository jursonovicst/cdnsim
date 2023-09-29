from typing import Iterator

import numpy as np

from cdnsim.arrival import ArrivalMixIn


class PoissonMixIn(ArrivalMixIn):
    """
    Implements a poisson based arrival process with **lam** arrival rate
    """

    def __init__(self, lam: float, **kwargs):
        super().__init__(**kwargs)
        self.__lam = lam

    @property
    def lam(self) -> float:
        return self.__lam

    @lam.setter
    def lam(self, v: float):
        if v <= 1:
            raise SyntaxError(f"lambda for poisson should be greater or equal to 1, got: {v}")
        self.__lam = v

    def _arrival(self) -> Iterator[int]:
        try:
            rng = np.random.default_rng()
            while True:
                yield rng.poisson(self.__lam, 1)[0]
        except KeyboardInterrupt:
            raise StopIteration
