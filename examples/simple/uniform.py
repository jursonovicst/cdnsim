from typing import Self

import pandas as pd
from scipy.stats import randint
import numpy as np

from cdnsim.requests.requests import Requests


class Uniform(Requests):
    """
    Implements a Uniform distribution based request profile.
    """

    def __init__(self, cbase: int):
        """
        :param cbase: number of content
        """
        super().__init__(None)
        self._cbase = cbase

    def generate(self, k: int) -> Self:
        r = np.unique(randint.rvs(1, self._cbase + 1, size=k), return_counts=True)
        return Requests(pd.Series(r[1], index=pd.MultiIndex.from_arrays([r[0], np.ones(self._cbase)], names=['content', 'size'])))
