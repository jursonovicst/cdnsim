from typing import List
from typing import Self

import pandas as pd

from cdnsim.requests import BaseRequests


class ThroughputRequests(BaseRequests):

    @classmethod
    def merge_requests(cls, dfs: List[Self]) -> Self:
        if len(dfs) == 0:
            raise ValueError("Cannot merge an empty DataFrame")

        return ThroughputRequests(pd.DataFrame(pd.concat(dfs)).groupby(['tick', 'content']).agg(
            freq=pd.NamedAgg(column="freq", aggfunc="sum"),
            size=pd.NamedAgg(column="size", aggfunc="min")
        ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tick' not in self.index.names:
            raise SyntaxError(f"'tick' must be part of the index names, got: {self.index.names}")
        if 'size' not in self.columns:
            raise SyntaxError(f"'size' must be part of the columns, got: {self.columns}")

    @property
    def rpt(self) -> pd.Series:
        return self.freq.groupby('tick').sum()

    @property
    def bpt(self) -> pd.Series:
        return self.prod(axis=1).groupby('tick').sum()
