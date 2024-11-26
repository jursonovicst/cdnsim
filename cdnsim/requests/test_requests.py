from unittest import TestCase

import pandas as pd

from cdnsim.requests import BaseRequests, BaseSeries


class TestRequests(TestCase):
    def test_init(self):
        # init
        r1 = BaseRequests(data={'freq': [100, 200, 300]},
                          index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))
        r2 = BaseRequests(data={'freq': [10, 20, 30]},
                          index=pd.MultiIndex.from_arrays([[1, 2, 3], [22, 33, 44]], names=['content', 'dummy']))

        # split
        r = BaseRequests(data={'freq': [10, 2, 6]}, index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))

        d = r.split(1)
        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(1, len(d))
        self.assertEqual(r.freq.sum(), sum(map(lambda x: sum(x.freq), d)))
        self.assertListEqual([10, 2, 6], list(d[0].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))

        d = r.split(3)

        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        self.assertEqual(3, len(d))
        self.assertEqual(15, sum(map(lambda x: sum(x.freq), d)))
        self.assertListEqual([3, 0, 2], list(d[0].values))
        self.assertListEqual([3, 0, 2], list(d[1].values))
        self.assertListEqual([3, 0, 2], list(d[2].values))
        self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[1].index.levels[0]))
        self.assertListEqual([1, 2, 3], list(d[2].index.levels[0]))

        with self.assertRaises(ValueError):
            r.split(0)

        r = pd.DataFrame(data={'dummy': [1, 2, 3]})

        with self.assertRaises(AttributeError):
            r.requests.split(2)

        # # addition
        # s = r1 + BaseRequests(data={'freq': [1, 2, 3]}, index=pd.MultiIndex.from_arrays([[3, 4, 5]], names=['content']))
        #
        # self.assertListEqual([100, 200, 301, 2, 3], list(s.values))
        # self.assertListEqual(['content'], s.index.names)
        # self.assertListEqual([1, 2, 3, 4, 5], list(s.index.levels[0]))
        #
        # s = sum([r1, BaseRequests(data={'freq': [1, 2, 3]},
        #                           index=pd.MultiIndex.from_arrays([[3, 4, 5]], names=['content']))])
        #
        # self.assertListEqual([100, 200, 301, 2, 3], list(s.values))
        # self.assertListEqual(['content'], s.index.names)
        # self.assertListEqual([1, 2, 3, 4, 5], list(s.index.levels[0]))
        #
        # s = r1 + BaseRequests(data={'freq': []}, index=pd.MultiIndex.from_arrays([[]], names=['content']))
        #
        # self.assertListEqual([100, 200, 300], list(s.values))
        # self.assertListEqual(['content'], s.index.names)
        # self.assertListEqual([1, 2, 3], list(s.index.levels[0]))
        #
        # s = BaseRequests(data={'freq': []}, index=pd.MultiIndex.from_arrays([[], []], names=['content', 'dummy'])) + r2
        #
        # self.assertListEqual([10, 20, 30], list(s.values))
        # self.assertListEqual(['content', 'dummy'], s.index.names)
        # self.assertListEqual([1, 2, 3], list(s.index.levels[0]))
        # self.assertListEqual([22, 33, 44], list(s.index.levels[1]))
        #
        # with self.assertRaises(SyntaxError):
        #     r1 + r2
        #
        # # floor division
        # r = BaseRequests(data={'freq': [10, 2, 6]}, index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))
        #
        # with self.assertRaises(ValueError):
        #     r // 0
        #
        # with self.assertRaises(ValueError):
        #     r // 3.2
        #
        # d = r // 1
        # self.assertIsInstance(d, list)
        # self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        # self.assertEqual(1, len(d))
        # self.assertEqual(r.freq.sum(), sum(map(lambda x: sum(x.freq), d)))
        # self.assertListEqual([10, 2, 6], list(d[0].values))
        # self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        #
        # d = r // 3
        #
        # self.assertIsInstance(d, list)
        # self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        # self.assertEqual(3, len(d))
        # self.assertEqual(15, sum(map(lambda x: sum(x.freq), d)))
        # self.assertListEqual([3, 0, 2], list(d[0].values))
        # self.assertListEqual([3, 0, 2], list(d[1].values))
        # self.assertListEqual([3, 0, 2], list(d[2].values))
        # self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        # self.assertListEqual([1, 2, 3], list(d[1].index.levels[0]))
        # self.assertListEqual([1, 2, 3], list(d[2].index.levels[0]))
        #
        # # true division
        # r = BaseRequests(data={'freq': [10, 2, 6]}, index=pd.MultiIndex.from_arrays([[1, 2, 3]], names=['content']))
        #
        # with self.assertRaises(ValueError):
        #     r / 0
        #
        # with self.assertRaises(ValueError):
        #     r / 3.2
        #
        # d = r / 1
        # self.assertIsInstance(d, list)
        # self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        # self.assertEqual(1, len(d))
        # self.assertEqual(r.sum(), sum(map(sum, d)))
        # self.assertListEqual([10, 2, 6], list(d[0].values))
        # self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        #
        # d = r / 3
        #
        # self.assertIsInstance(d, list)
        # self.assertTrue(all([isinstance(i, BaseRequests) for i in d]), [type(i) for i in d])
        # self.assertEqual(3, len(d))
        # self.assertEqual(15, sum(map(sum, d)))
        # self.assertListEqual([3, 0, 2], list(d[0].values))
        # self.assertListEqual([3, 0, 2], list(d[1].values))
        # self.assertListEqual([3, 0, 2], list(d[2].values))
        # self.assertListEqual([1, 2, 3], list(d[0].index.levels[0]))
        # self.assertListEqual([1, 2, 3], list(d[1].index.levels[0]))
        # self.assertListEqual([1, 2, 3], list(d[2].index.levels[0]))

    def test_custom(self):
        class MyBaseSeries(BaseSeries):
            @property
            def _constructor_expanddim(self):
                return MyBaseRequests

        class MyBaseRequests(BaseRequests):
            @property
            def _constructor_sliced(self):
                return MyBaseSeries

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if 'dummyi' not in self.index.names:
                    raise SyntaxError(f"'dummyi' must be part of the index names, got: {self.index.names}")
                if 'dummyc' not in self.columns:
                    raise SyntaxError(f"'dummyc' must be part of the columns, got: {self.columns}")

        r1 = MyBaseRequests({'freq': [1, 2, 3], 'dummyc': [4, 5, 6]},
                            index=pd.MultiIndex.from_arrays([['c1', 'c2', 'c3'], [10, 20, 30]],
                                                            names=['content', 'dummyi']))
        self.assertEqual(6, r1.freq.sum())

        # default methods
        self.assertIsInstance(r1.sort_values('freq', ascending=False), MyBaseRequests)
        self.assertIsInstance(r1[['freq', 'dummyc']], MyBaseRequests)
