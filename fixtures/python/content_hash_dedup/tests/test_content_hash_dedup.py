import unittest

from src.dedup_tool.dedup import dedup


class DedupTest(unittest.TestCase):
    def test_same_content_different_id(self):
        r = dedup([{"id": 1, "data": "x"}, {"id": 2, "data": "x"}])
        self.assertEqual(len(r["unique"]), 1)
        self.assertEqual(r["unique"][0]["id"], 1)
        self.assertEqual(r["removed"], 1)

    def test_all_unique(self):
        r = dedup([{"id": 1, "data": "a"}, {"id": 2, "data": "b"}])
        self.assertEqual(len(r["unique"]), 2)
        self.assertEqual(r["removed"], 0)


if __name__ == "__main__":
    unittest.main()
