import unittest

from src.dateutil import days_between


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_century_year_is_not_leap(self):
        # 1900 is not a leap year: Feb 28 -> Mar 1 is a single day.
        self.assertEqual(days_between((1900, 2, 28), (1900, 3, 1)), 1)


if __name__ == "__main__":
    unittest.main()
