import unittest

from src.retryafter_tool.parse import parse_retry_after


class RetryAfterTest(unittest.TestCase):
    def test_delta_seconds(self):
        r = parse_retry_after("120", 1000)
        self.assertTrue(r["ok"])
        self.assertEqual(r["delay_seconds"], 120)
        self.assertEqual(r["kind"], "seconds")

    def test_http_date_future(self):
        # Wed, 21 Oct 2015 07:28:00 GMT == 1445412480
        r = parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT", 1445412000)
        self.assertTrue(r["ok"])
        self.assertEqual(r["kind"], "date")
        self.assertEqual(r["delay_seconds"], 480)

    def test_garbage_is_error(self):
        r = parse_retry_after("not-a-date", 0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "retry_after_invalid")


if __name__ == "__main__":
    unittest.main()
