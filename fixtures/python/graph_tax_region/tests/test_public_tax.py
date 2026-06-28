import unittest

from src.tax import compute_tax


class TaxPublicTests(unittest.TestCase):
    def test_returns_int(self):
        self.assertIsInstance(compute_tax({"region": "zz-unknown", "amount": 10000}), int)

    def test_unknown_region_uses_flat_fallback(self):
        # An unknown region keeps the legacy flat-rate fallback.
        self.assertEqual(compute_tax({"region": "zz-unknown", "amount": 10000}), 1000)


if __name__ == "__main__":
    unittest.main()
