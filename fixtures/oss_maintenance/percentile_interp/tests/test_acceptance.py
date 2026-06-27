import unittest

from src.stats import percentile


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_median_of_even_list(self):
        self.assertEqual(percentile([1, 2, 3, 4], 50), 2.5)


if __name__ == "__main__":
    unittest.main()
