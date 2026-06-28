import unittest

from src.dotenv_tool.parse import parse


class DotenvTest(unittest.TestCase):
    def test_basic(self):
        r = parse("A=1\nB=2")
        self.assertEqual(r["env"], {"A": "1", "B": "2"})

    def test_quotes(self):
        r = parse('A="hello"')
        self.assertEqual(r["env"], {"A": "hello"})


if __name__ == "__main__":
    unittest.main()
