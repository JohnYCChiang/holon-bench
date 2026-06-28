import unittest

from src.glob_tool.translate import matches


class GlobTest(unittest.TestCase):
    def test_star(self):
        self.assertTrue(matches("*.py", "main.py"))
        self.assertFalse(matches("*.py", "main.txt"))

    def test_literal_dot(self):
        self.assertFalse(matches("a.b", "axb"))

    def test_question(self):
        self.assertTrue(matches("a?c", "abc"))


if __name__ == "__main__":
    unittest.main()
