from unittest import TestCase

import pandas as pd

from cdnsim.requests import Requests


class TestRequests(TestCase):
    def test_init(self):
        r = Requests(pd.Series([100, 200, 300],
                               index=pd.MultiIndex.from_arrays([[1, 2, 3], [10, 20, 30]], names=('content', 'size'))))

        self.assertEqual(600, r.nrequests)
        self.assertEqual(14000, r.bytes)

        s = r + Requests(pd.Series([1, 2, 3], name='name_ignored',
                                   index=pd.MultiIndex.from_arrays([[3, 4, 5], [30, 40, 50]],
                                                                   names=('content', 'size'))))

        self.assertListEqual([100, 200, 301, 2, 3], list(s._freq.values))
        self.assertListEqual([1, 2, 3, 4, 5], list(s._freq.index.levels[0]))
        self.assertListEqual([10, 20, 30, 40, 50], list(s._freq.index.levels[1]))

        r = Requests(pd.Series([10, 2, 6],
                               index=pd.MultiIndex.from_arrays([[1, 2, 3], [10, 20, 30]], names=('content', 'size'))))
        d = r / 3

        self.assertEqual(3, len(d))
        self.assertListEqual([3, 0, 2], list(d[0]._freq.values))
        self.assertListEqual([4, 1, 2], list(d[1]._freq.values))
        self.assertListEqual([3, 1, 2], list(d[2]._freq.values))
