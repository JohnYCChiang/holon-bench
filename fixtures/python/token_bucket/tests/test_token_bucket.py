import unittest

from src.ratelimit_tool.bucket import TokenBucket


class TokenBucketTest(unittest.TestCase):
    def test_consume_then_deny_then_refill(self):
        b = TokenBucket(capacity=2, refill_per_sec=1)
        self.assertTrue(b.allow(now=0)["allowed"])
        self.assertTrue(b.allow(now=0)["allowed"])
        self.assertFalse(b.allow(now=0)["allowed"])
        self.assertTrue(b.allow(now=1)["allowed"])

    def test_remaining_reported(self):
        b = TokenBucket(capacity=2, refill_per_sec=1)
        self.assertEqual(b.allow(now=0)["remaining"], 1.0)
        self.assertEqual(b.allow(now=0)["remaining"], 0.0)


if __name__ == "__main__":
    unittest.main()
