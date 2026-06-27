import unittest

from src.intervals import merge


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_touching_intervals_merge(self):
        self.assertEqual(merge([[1, 2], [2, 3]]), [[1, 3]])


if __name__ == "__main__":
    unittest.main()
