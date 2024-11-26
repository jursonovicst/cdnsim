from unittest import TestCase

import pandas as pd

from throughput import ThroughputRequests


class TestThroughputRequests(TestCase):
    def test_merge_requests(self):
        r1 = ThroughputRequests(data={'freq': [1, 2, 3, 4, 5, 6], 'size': [10, 20, 30, 10, 20, 30]},
                                index=pd.MultiIndex.from_arrays(
                                    [[0, 0, 0, 1, 1, 1], ['c1', 'c2', 'c3', 'c1', 'c2', 'c3']],
                                    names=['tick', 'content']))
        r2 = ThroughputRequests(data={'freq': [60, 70, 80, 90, 100, 110], 'size': [30, 40, 50, 30, 40, 50]},
                                index=pd.MultiIndex.from_arrays(
                                    [[1, 1, 1, 2, 2, 2], ['c3', 'c4', 'c5', 'c3', 'c4', 'c5']],
                                    names=['tick', 'content']))

        s = ThroughputRequests.merge_requests([r1, r2])
        self.skipTest("Implement me")
        # self.assertEqual(66, s[(1,'c3'):'freq'])
        # print(s)
