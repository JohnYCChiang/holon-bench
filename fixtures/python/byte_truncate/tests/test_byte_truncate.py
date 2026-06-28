import unittest

from src.truncate_tool.truncate import truncate_bytes


class ByteTruncateTest(unittest.TestCase):
    def test_ascii_truncation(self):
        r = truncate_bytes("hello world", 5)
        self.assertEqual(r["text"], "hello")
        self.assertTrue(r["truncated"])
        self.assertEqual(r["byte_count"], 5)
        self.assertEqual(r["omitted_bytes"], 6)

    def test_byte_count_matches_encoded_length(self):
        r = truncate_bytes("ab" + "é" * 5, 3)
        encoded = r["text"].encode("utf-8")
        self.assertLessEqual(len(encoded), 3)
        self.assertEqual(r["byte_count"], len(encoded))
        self.assertEqual(r["text"], "ab")

    def test_no_truncation_when_within_budget(self):
        r = truncate_bytes("abc", 10)
        self.assertFalse(r["truncated"])
        self.assertEqual(r["text"], "abc")


if __name__ == "__main__":
    unittest.main()
