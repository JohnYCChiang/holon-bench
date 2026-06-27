import unittest

from engine import gate, load_thresholds


class ThresholdTests(unittest.TestCase):
    def setUp(self):
        self.thresholds = load_thresholds()

    def test_low_coverage_is_rejected(self):
        # High score but poor coverage must not pass — coverage is ungated.
        self.assertEqual(gate(self.thresholds, {"score": 95, "coverage": 0.40}), "reject")

    def test_good_submission_accepted(self):
        self.assertEqual(gate(self.thresholds, {"score": 95, "coverage": 0.90}), "accept")


if __name__ == "__main__":
    unittest.main()
