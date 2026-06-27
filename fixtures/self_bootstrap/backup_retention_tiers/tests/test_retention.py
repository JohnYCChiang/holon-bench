import unittest

from engine import keep_interval, load_retention


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_retention()

    def test_two_month_old_kept(self):
        self.assertEqual(keep_interval(self.cfg, 60), 30)

    def test_ancient_dropped(self):
        self.assertIsNone(keep_interval(self.cfg, 400))


if __name__ == "__main__":
    unittest.main()
