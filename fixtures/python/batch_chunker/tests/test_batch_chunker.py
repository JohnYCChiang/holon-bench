import unittest

from src.chunk_tool.chunk import chunk


class ChunkTest(unittest.TestCase):
    def test_partial_last_batch(self):
        r = chunk([1, 2, 3, 4, 5], 2)
        self.assertTrue(r["ok"])
        self.assertEqual(r["batches"], [[1, 2], [3, 4], [5]])
        self.assertEqual(r["count"], 3)

    def test_empty(self):
        r = chunk([], 3)
        self.assertEqual(r["batches"], [])
        self.assertEqual(r["count"], 0)

    def test_invalid_size(self):
        r = chunk([1], 0)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_size")


if __name__ == "__main__":
    unittest.main()
