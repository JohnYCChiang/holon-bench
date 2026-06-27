import unittest

from engine import is_overcommitted, load_config, quota_for


class QuotaTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_tenant_c_has_quota(self):
        self.assertGreaterEqual(quota_for(self.config, "tenant_c"), 20)

    def test_pool_not_overcommitted(self):
        self.assertFalse(is_overcommitted(self.config))


if __name__ == "__main__":
    unittest.main()
