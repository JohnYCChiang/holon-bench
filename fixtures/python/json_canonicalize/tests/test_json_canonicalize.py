import unittest

from src.canon_tool.canon import canonicalize


class CanonTest(unittest.TestCase):
    def test_sorted_compact(self):
        r = canonicalize({"b": 1, "a": 2})
        self.assertEqual(r["text"], '{"a":2,"b":1}')

    def test_nested_no_spaces(self):
        r = canonicalize({"x": [1, {"z": 1, "y": 2}]})
        self.assertEqual(r["text"], '{"x":[1,{"y":2,"z":1}]}')


if __name__ == "__main__":
    unittest.main()
