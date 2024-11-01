from typing import Self
from scipy.stats import zipfian
import pandas as pd
from .requests import Requests


class Zipf(Requests):
    def __init__(self, cbase: int, a: float):
        super().__init__(None)
        self._cbase = cbase
        self._a = a

    def generate(self, k:int) -> Self:
        return Requests(pd.Series(zipfian.rvs(self._a, self._cbase, size=k)).value_counts())
