from unittest import TestCase

from cdnsim.arrival import Arrival


class TestArrival(TestCase):
    def test_tick(self):
        a = Arrival(ticks=5)
        with self.assertRaises(AttributeError):
            self.assertEqual(0, a.tick)

        i = 0
        for v in a:
            self.assertIsNone(v)
            self.assertEqual(i, a.tick)
            i += 1
        self.assertEqual(5, i)

        with self.assertRaises(AttributeError):
            self.assertEqual(0, a.tick)
