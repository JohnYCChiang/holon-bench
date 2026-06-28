import unittest

from src.globsel_tool.select import select_paths


class GlobSelectTest(unittest.TestCase):
    def test_include_glob(self):
        r = select_paths(["a.py", "b.txt", "c.py"], ["*.py"], [])
        self.assertTrue(r["ok"])
        self.assertEqual(r["selected"], ["a.py", "c.py"])

    def test_exclude_removes(self):
        r = select_paths(["a.py", "test_a.py"], ["*.py"], ["test_*"])
        self.assertEqual(r["selected"], ["a.py"])
        self.assertEqual(r["excluded"], ["test_a.py"])


if __name__ == "__main__":
    unittest.main()
