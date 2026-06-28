import unittest

from src.feature import payments_v2_enabled


class FeaturePublicTests(unittest.TestCase):
    def test_payments_v2_enabled_is_bool(self):
        self.assertIsInstance(payments_v2_enabled(), bool)


if __name__ == "__main__":
    unittest.main()
