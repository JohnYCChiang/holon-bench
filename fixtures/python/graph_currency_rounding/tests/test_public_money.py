import unittest

from src.money import format_amount


class MoneyPublicTests(unittest.TestCase):
    def test_returns_str(self):
        self.assertIsInstance(format_amount(1.25, "USD"), str)

    def test_usd_two_decimals(self):
        # USD keeps the two-decimal default precision.
        self.assertEqual(format_amount(1.5, "USD"), "1.50")


if __name__ == "__main__":
    unittest.main()
