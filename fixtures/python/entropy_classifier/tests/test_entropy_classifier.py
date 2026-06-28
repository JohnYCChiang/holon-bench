import unittest

from src.entropy_tool.check import classify


class EntropyTest(unittest.TestCase):
    def test_high_entropy_long_is_secret(self):
        r = classify("aB3xY7zQ9mK2pL5w")
        self.assertTrue(r["ok"])
        self.assertTrue(r["likely_secret"])

    def test_short_high_entropy_not_secret(self):
        r = classify("aB3x")
        self.assertFalse(r["likely_secret"])

    def test_low_entropy(self):
        r = classify("aaaaaaaaaaaaaaaa")
        self.assertEqual(r["entropy"], 0.0)
        self.assertFalse(r["likely_secret"])


if __name__ == "__main__":
    unittest.main()
