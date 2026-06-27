import unittest

from engine import is_allowed, load_allow


class EnvAllowTests(unittest.TestCase):
    def setUp(self):
        self.allow = load_allow()

    def test_ci_exposed(self):
        self.assertTrue(is_allowed(self.allow, "build", "CI"))

    def test_secret_hidden(self):
        self.assertFalse(is_allowed(self.allow, "build", "AWS_SECRET_KEY"))


if __name__ == "__main__":
    unittest.main()
