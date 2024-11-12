from typing import Self

import pandas as pd
from scipy.stats import randint

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
        return Requests(pd.Series(randint.rvs(1, self._cbase + 1, size=k)).value_counts())
