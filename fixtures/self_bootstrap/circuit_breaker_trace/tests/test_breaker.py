import unittest

from engine import load_json, replay


class BreakerTests(unittest.TestCase):
    def setUp(self):
        self.config = load_json("breaker.json")
        self.outcomes = load_json("failed_run.json")["outcomes"]

    def test_recorded_run_does_not_trip(self):
        self.assertFalse(replay(self.config, self.outcomes)["tripped"])

    def test_sustained_failure_still_trips(self):
        # Disabling the breaker (infinite threshold) is the wrong fix.
        self.assertTrue(replay(self.config, ["fail"] * 20)["tripped"])


if __name__ == "__main__":
    unittest.main()
