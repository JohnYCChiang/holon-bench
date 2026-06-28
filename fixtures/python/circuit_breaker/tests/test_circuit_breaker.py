import unittest

from src.breaker_tool.breaker import CircuitBreaker


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class BreakerTest(unittest.TestCase):
    def test_opens_after_threshold(self):
        c = Clock()
        b = CircuitBreaker(3, 5.0, c)
        for _ in range(3):
            b.record_failure()
        self.assertEqual(b.state(), "open")
        self.assertFalse(b.allow())

    def test_half_open_at_boundary(self):
        c = Clock()
        b = CircuitBreaker(3, 5.0, c)
        for _ in range(3):
            b.record_failure()
        c.t = 5.0
        self.assertTrue(b.allow())
        self.assertEqual(b.state(), "half_open")


if __name__ == "__main__":
    unittest.main()
