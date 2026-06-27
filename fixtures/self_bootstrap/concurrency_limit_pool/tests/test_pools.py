import unittest

from engine import capacity, is_valid, load_pools, pool_for


class PoolTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_pools()

    def test_realtime_has_priority_pool(self):
        self.assertEqual(pool_for(self.cfg, "realtime"), "priority")
        self.assertGreaterEqual(capacity(self.cfg, "priority"), 2)

    def test_plan_valid(self):
        self.assertTrue(is_valid(self.cfg))


if __name__ == "__main__":
    unittest.main()
