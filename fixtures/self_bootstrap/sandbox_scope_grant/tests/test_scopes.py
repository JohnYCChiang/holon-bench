import unittest

from engine import allowed, load_scopes


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.scopes = load_scopes()

    def test_registry_fetch_allowed(self):
        self.assertTrue(allowed(self.scopes, "ci_runner", "net:fetch:registry"))

    def test_internal_fetch_still_denied(self):
        self.assertFalse(allowed(self.scopes, "ci_runner", "net:fetch:internal"))


if __name__ == "__main__":
    unittest.main()
