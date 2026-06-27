import unittest

from src.htmlesc import escape


class AcceptanceTests(unittest.TestCase):
    def test_does_not_double_escape(self):
        self.assertEqual(escape("a < b"), "a &lt; b")


if __name__ == "__main__":
    unittest.main()
