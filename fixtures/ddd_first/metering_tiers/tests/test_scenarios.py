import unittest

from src.metering import TieredPlan, MeteredSubscription


class Metering(unittest.TestCase):
    def test_tiered_cost(self):
        plan = TieredPlan(((100, 5), (None, 2)))  # first 100 @5, rest @2
        sub = MeteredSubscription(plan)
        sub.record(150)
        # 100*5 + 50*2 = 600
        self.assertEqual(sub.current_charge(), 600)

    def test_close_cycle_resets_usage(self):
        plan = TieredPlan(((None, 3),))
        sub = MeteredSubscription(plan)
        sub.record(10)
        self.assertEqual(sub.close_cycle(), 30)
        self.assertEqual(sub.usage, 0)


if __name__ == "__main__":
    unittest.main()
