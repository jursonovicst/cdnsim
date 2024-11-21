from typing import Self, Hashable, List
from unittest import TestCase

from cdnsim.requests import Requests


class TestRequests(TestCase):
    def test_init(self):
        # init
        r1 = Requests(freqs=[100, 200, 300], index={'content': [1, 2, 3]})
        r2 = Requests(freqs=[100, 200, 300], index={'content': [1, 2, 3], 'dummy': [22, 33, 44]})

        # properties
        self.assertEqual(600, r1.nrequests)
        self.assertListEqual(['content'], r1.index.names)
        self.assertEqual(600, r2.nrequests)
        self.assertListEqual(['content', 'dummy'], r2.index.names)
        # self.assertEqual(14000, r.pmf, r.pmf)

        # addition
        s = r1 + Requests(freqs=[1, 2, 3], index={'content': [3, 4, 5]})

        self.assertListEqual([100, 200, 301, 2, 3], list(s.values))
        self.assertListEqual(['content'], s.index.names)
        self.assertListEqual([1, 2, 3, 4, 5], list(s.index.levels[0]))

        # division
        r = Requests(freqs=[10, 2, 6], index={'content': [1, 2, 3]})
        d = r // 3

        self.assertIsInstance(d, list)
        self.assertTrue(all([isinstance(i, Requests) for i in d]), [type(i) for i in d])
        self.assertEqual(3, len(d))
        self.assertEqual(r.sum(), sum(map(sum, d)))
        self.assertListEqual([3, 0, 2], list(d[0]))
        self.assertListEqual([4, 1, 2], list(d[1]))
        self.assertListEqual([3, 1, 2], list(d[2]))

    def test_custom(self):
        class MyRequests(Requests):
            @classmethod
            def generate(cls, k: int) -> Self:
                return cls([k], {'content': ['c']})

        myrequests = MyRequests.generate(10)
        self.assertIsInstance(myrequests, Requests)
        self.assertEqual(10, myrequests.sum())
