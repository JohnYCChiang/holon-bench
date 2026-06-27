import unittest

from src.lru import LRUCache


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_get_refreshes_recency(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.get("a"), 1)  # "a" is now most-recently used
        c.put("c", 3)  # cache full -> evict "b", keep "a"
        self.assertEqual(c.get("a"), 1)
        self.assertIsNone(c.get("b"))


if __name__ == "__main__":
    unittest.main()
