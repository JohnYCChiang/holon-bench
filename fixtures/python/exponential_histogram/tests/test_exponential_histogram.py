import unittest

from src.histo_tool.histogram import histogram


class HistoTest(unittest.TestCase):
    def test_base2(self):
        r = histogram([1, 2, 3, 4], 2)
        self.assertEqual(r["buckets"], [[0, 1], [1, 2], [2, 1]])
        self.assertEqual(r["total"], 4)

    def test_invalid_value(self):
        r = histogram([0], 2)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_value")


if __name__ == "__main__":
    unittest.main()
