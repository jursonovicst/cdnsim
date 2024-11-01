from .arrival import Arrival
import numpy as np

class Poisson(Arrival):
    def __init__(self, lam: float, **kwargs):
        super().__init__(**kwargs)
        if lam <= 1:
            raise ValueError(f"lambda for poisson should be greater or equal to 1, got: {lam}")
        self.__lam = lam
        self.__rng = np.random.default_rng()

    def __next__(self) -> int:
        return self.__rng.poisson(self.__lam, 1)[0]
