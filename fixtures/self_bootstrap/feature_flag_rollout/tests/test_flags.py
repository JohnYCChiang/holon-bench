import unittest

from engine import is_enabled, load_flags


class FeatureFlagTests(unittest.TestCase):
    def setUp(self):
        self.flags = load_flags()

    def test_allowlisted_user_sees_flag(self):
        self.assertTrue(is_enabled(self.flags, "internal_metrics", "ops_admin"))

    def test_regular_user_does_not(self):
        self.assertFalse(is_enabled(self.flags, "internal_metrics", "random_user_42"))


if __name__ == "__main__":
    unittest.main()
