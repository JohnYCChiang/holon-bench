import unittest

from src.redact_tool.redact import redact


class RedactTest(unittest.TestCase):
    def test_counts_all_matches(self):
        r = redact("a1 b2 c3", [r"\d"])
        self.assertEqual(r["text"], "a[REDACTED] b[REDACTED] c[REDACTED]")
        self.assertEqual(r["count"], 3)

    def test_no_match(self):
        r = redact("clean", [r"\d"])
        self.assertEqual(r["count"], 0)


if __name__ == "__main__":
    unittest.main()
