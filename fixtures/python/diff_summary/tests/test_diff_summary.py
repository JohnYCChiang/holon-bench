import unittest

from src.diff_tool.summarize import summarize_diff


class DiffSummaryTest(unittest.TestCase):
    def test_simple_add(self):
        r = summarize_diff(["a", "b"], ["a", "b", "c"])
        self.assertTrue(r["ok"])
        self.assertEqual(r["added"], 1)
        self.assertEqual(r["removed"], 0)
        self.assertEqual(r["unchanged"], 2)
        self.assertTrue(r["changed"])

    def test_identical(self):
        r = summarize_diff(["a", "b"], ["a", "b"])
        self.assertEqual(r["unchanged"], 2)
        self.assertFalse(r["changed"])


if __name__ == "__main__":
    unittest.main()
