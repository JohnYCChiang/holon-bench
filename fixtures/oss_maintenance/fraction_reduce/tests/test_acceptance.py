import unittest

from src.fraction import reduce_fraction


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_negative_denominator_normalized(self):
        self.assertEqual(reduce_fraction(1, -2), (-1, 2))


if __name__ == "__main__":
    unittest.main()
