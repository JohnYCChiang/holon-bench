import unittest

from engine import delivers, load_subscriptions, subscribers


class SubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.subs = load_subscriptions()

    def test_deployments_gets_release(self):
        self.assertTrue(delivers(self.subs, "release.published", "deployments"))

    def test_deployments_not_user_deleted(self):
        self.assertFalse(delivers(self.subs, "user.deleted", "deployments"))


if __name__ == "__main__":
    unittest.main()
