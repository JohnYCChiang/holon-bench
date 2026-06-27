import unittest

from engine import load_json, process


class IdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_json("idempotency.json")
        self.events = load_json("failed_run.json")["events"]

    def test_recorded_retry_deduped(self):
        self.assertEqual(process(self.cfg, self.events), ["accepted", "duplicate"])

    def test_distinct_keys_accepted(self):
        result = process(self.cfg, [{"key": "a", "ts": 0}, {"key": "b", "ts": 0}])
        self.assertEqual(result, ["accepted", "accepted"])


if __name__ == "__main__":
    unittest.main()
