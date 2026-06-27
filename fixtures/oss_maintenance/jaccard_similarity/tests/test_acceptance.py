import unittest

from src.jaccard import jaccard


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_overlapping_sets(self):
        self.assertAlmostEqual(jaccard(["a", "b"], ["b", "c"]), 1 / 3)


if __name__ == "__main__":
    unittest.main()
