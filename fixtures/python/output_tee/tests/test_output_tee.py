import unittest
import io

from src.tee_tool.tee import tee


class TeeTest(unittest.TestCase):
    def test_two_sinks(self):
        a, b = io.StringIO(), io.StringIO()
        r = tee(["ab", "cd"], [a, b])
        self.assertEqual(a.getvalue(), "abcd")
        self.assertEqual(b.getvalue(), "abcd")
        self.assertEqual(r["bytes"], 4)
        self.assertEqual(r["chunks"], 2)

    def test_empty_chunks(self):
        a = io.StringIO()
        r = tee([], [a])
        self.assertEqual(r["bytes"], 0)
        self.assertEqual(r["chunks"], 0)


if __name__ == "__main__":
    unittest.main()
