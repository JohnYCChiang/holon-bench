import unittest

from src.naming import resource_name


class NamingPublicTests(unittest.TestCase):
    def test_returns_str(self):
        self.assertIsInstance(resource_name({"env": "prod", "team": "pay", "name": "api"}), str)

    def test_missing_env_falls_back_to_name(self):
        # Without both env and team, the legacy bare name is returned unchanged.
        self.assertEqual(resource_name({"team": "pay", "name": "Api"}), "Api")


if __name__ == "__main__":
    unittest.main()
