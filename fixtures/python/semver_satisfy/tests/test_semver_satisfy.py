import unittest

from src.semver_tool.satisfy import satisfies


class SemverTest(unittest.TestCase):
    def test_gte(self):
        self.assertTrue(satisfies("1.2.3", ">=1.0.0")["match"])

    def test_caret_upper_excluded(self):
        self.assertFalse(satisfies("2.0.0", "^1.2.3")["match"])

    def test_exact(self):
        self.assertTrue(satisfies("1.2.3", "1.2.3")["match"])
        self.assertFalse(satisfies("1.2.4", "1.2.3")["match"])


if __name__ == "__main__":
    unittest.main()
