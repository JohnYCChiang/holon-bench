import unittest

from src.path_tool.relativize import relativize


class RelTest(unittest.TestCase):
    def test_child(self):
        r = relativize("/a/b/c", "/a/b")
        self.assertEqual(r["rel"], "c")

    def test_same(self):
        r = relativize("/a/b", "/a/b")
        self.assertEqual(r["rel"], ".")

    def test_not_absolute(self):
        r = relativize("a/b", "/a")
        self.assertFalse(r["ok"])


if __name__ == "__main__":
    unittest.main()
