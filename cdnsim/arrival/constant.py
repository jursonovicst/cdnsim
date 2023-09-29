import numpy as np

from cdnsim.arrival import ArrivalMixIn


class ConstantMixIn(ArrivalMixIn):
    """
    Implements a constant arrival process.
    """

    def __init__(self, rate: float):
        self.__rate = rate

    def _arrival(self, size: int = 1) -> np.ndarray:
        return np.ones(size) * int(self.__rate)
        # TODO: fix this to round to integer correctly (rate 1.1: [1 1 1 1 1 1 1 1 1 2])
