import unittest

from engine import get_ttl, load_config


class TtlTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_auth_token_is_short_lived(self):
        ttl = get_ttl(self.config, "auth_token")
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 60)

    def test_static_asset_unchanged(self):
        self.assertEqual(get_ttl(self.config, "static_asset"), 86400)


if __name__ == "__main__":
    unittest.main()
