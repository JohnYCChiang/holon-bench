import unittest

from src.money import round_half_up


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_half_rounds_away_from_zero(self):
        self.assertEqual(round_half_up("2.5", 0), "3")
        self.assertEqual(round_half_up("0.125", 2), "0.13")


if __name__ == "__main__":
    unittest.main()
