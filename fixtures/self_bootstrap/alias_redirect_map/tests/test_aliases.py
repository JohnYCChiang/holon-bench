import unittest

from engine import load_aliases, resolve


class AliasTests(unittest.TestCase):
    def setUp(self):
        self.aliases = load_aliases()

    def test_deploy_resolves_to_canonical(self):
        self.assertEqual(resolve(self.aliases, "deploy"), "release_v2")

    def test_release_unchanged(self):
        self.assertEqual(resolve(self.aliases, "release"), "release_v2")


if __name__ == "__main__":
    unittest.main()
