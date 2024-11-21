from typing import Self

import pandas as pd
from scipy.stats import zipfian

from cdnsim.requests.requests import BaseRequests


class Zipf(BaseRequests):
    """
    Implements a Zipf distribution based request profile.
    """

    def __init__(self, cbase: int, a: float):
        """
        :param cbase: number of content
        :param a: zipf distribution parameter
        """
        super().__init__(None)
        self._cbase = cbase
        self._a = a

    def generate(self, k: int) -> Self:
        return BaseRequests(pd.Series(zipfian.rvs(self._a, self._cbase, size=k)).value_counts())
