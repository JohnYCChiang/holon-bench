import unittest

from src.retry import RetryBudget


class RetryBudgets(unittest.TestCase):
    def test_trips_open_after_max_failures(self):
        rb = RetryBudget(max_failures=2, cooldown=10)
        rb.record_failure(0)
        rb.record_failure(1)
        self.assertEqual(rb.state, "OPEN")
        self.assertEqual(rb.events, ["Opened"])
        self.assertFalse(rb.allow(5))

    def test_success_resets_failures_when_closed(self):
        rb = RetryBudget(max_failures=3, cooldown=10)
        rb.record_failure(0)
        rb.record_success(1)
        self.assertEqual(rb.failures, 0)
        self.assertEqual(rb.state, "CLOSED")


if __name__ == "__main__":
    unittest.main()
