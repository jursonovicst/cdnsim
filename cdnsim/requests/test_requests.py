from typing import Self
from unittest import TestCase

import pandas as pd

from cdnsim.requests import BaseRequests


class TestRequests(TestCase):
    def test_init(self):
        # init
        r1 = BaseRequests(data=[100, 200, 300], index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))
        r2 = BaseRequests(data=[10, 20, 30],
                          index=pd.MultiIndex.from_arrays([[1, 2, 3], [22, 33, 44]], names=['content', 'dummy']))

        # properties
        self.assertEqual(600, r1.sum())
        self.assertEqual(60, r2.sum())

        # addition
        s = r1 + BaseRequests(data=[1, 2, 3], index=pd.MultiIndex.from_arrays([[3, 4, 5]], names=['content']))

        self.assertListEqual([100, 200, 301, 2, 3], list(s.values))
        self.assertListEqual(['content'], s.index.names)
        self.assertListEqual([1, 2, 3, 4, 5], list(s.index.levels[0]))

        s = sum([r1, BaseRequests(data=[1, 2, 3], index=pd.MultiIndex.from_arrays([[3, 4, 5]], names=['content']))])

        self.assertListEqual([100, 200, 301, 2, 3], list(s.values))
        self.assertListEqual(['content'], s.index.names)
        self.assertListEqual([1, 2, 3, 4, 5], list(s.index.levels[0]))

        s = r1 + BaseRequests(data=[], index=pd.MultiIndex.from_arrays([[]], names=['content']))

        self.assertListEqual([100, 200, 300], list(s.values))
        self.assertListEqual(['content'], s.index.names)
        self.assertListEqual([1, 2, 3], list(s.index.levels[0]))

        s = BaseRequests(data=[], index=pd.MultiIndex.from_arrays([[], []], names=['content', 'dummy'])) + r2

        self.assertListEqual([10, 20, 30], list(s.values))
        self.assertListEqual(['content', 'dummy'], s.index.names)
        self.assertListEqual([1, 2, 3], list(s.index.levels[0]))
        self.assertListEqual([22, 33, 44], list(s.index.levels[1]))

        with self.assertRaises(SyntaxError):
            r1 + r2

        # floor division
        r = BaseRequests(data=[10, 2, 6], index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))

        with self.assertRaises(ValueError):
            r // 0

        with self.assertRaises(ValueError):
            r // 3.2

        d = r // 1
        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(1, len(d))
        self.assertEqual(r.sum(), sum(map(sum, d)))
        self.assertListEqual([10, 2, 6], list(d[0].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))

        d = r // 3

        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(3, len(d))
        self.assertEqual(15, sum(map(sum, d)))
        self.assertListEqual([3, 0, 2], list(d[0].values))
        self.assertListEqual([3, 0, 2], list(d[1].values))
        self.assertListEqual([3, 0, 2], list(d[2].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[1].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[2].index.levels[0]))

        # true division
        r = BaseRequests(data=[10, 2, 6], index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))

        with self.assertRaises(ValueError):
            r / 0

        with self.assertRaises(ValueError):
            r / 3.2

        d = r / 1
        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(1, len(d))
        self.assertEqual(r.sum(), sum(map(sum, d)))
        self.assertListEqual([10, 2, 6], list(d[0].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))

        d = r / 3

        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(3, len(d))
        self.assertEqual(15, sum(map(sum, d)))
        self.assertListEqual([3, 0, 2], list(d[0].values))
        self.assertListEqual([3, 0, 2], list(d[1].values))
        self.assertListEqual([3, 0, 2], list(d[2].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[1].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[2].index.levels[0]))

    def test_custom(self):
        class MyBaseRequests(BaseRequests):
            @classmethod
            def generate(cls, k: int) -> Self:
                return MyBaseRequests(data=[k], index=pd.MultiIndex.from_arrays([['c']], names=['content']))

        myrequests = MyBaseRequests.generate(10)
        self.assertIsInstance(myrequests, BaseRequests)
        self.assertEqual(10, myrequests.sum())
