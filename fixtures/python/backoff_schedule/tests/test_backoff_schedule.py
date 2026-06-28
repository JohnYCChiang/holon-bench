import unittest

from src.backoff_tool.schedule import compute_backoff


class BackoffScheduleTest(unittest.TestCase):
    def test_first_attempt_is_base(self):
        r = compute_backoff(1)
        self.assertTrue(r["ok"])
        self.assertEqual(r["delay_ms"], 100)
        self.assertFalse(r["capped"])

    def test_second_attempt_doubles(self):
        self.assertEqual(compute_backoff(2)["delay_ms"], 200)

    def test_large_attempt_is_capped(self):
        r = compute_backoff(20)
        self.assertEqual(r["delay_ms"], 2000)
        self.assertTrue(r["capped"])

    def test_invalid_attempt_is_error(self):
        r = compute_backoff(0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_attempt")


if __name__ == "__main__":
    unittest.main()
