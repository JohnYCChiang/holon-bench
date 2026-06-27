import unittest

from engine import escalate, load_policy


class EscalationTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()

    def test_repeated_failures_page_oncall(self):
        # After five failures the on-call must be paged, but the policy caps out at notify_team.
        self.assertEqual(escalate(self.policy, 5), "page_oncall")

    def test_existing_tiers_preserved(self):
        self.assertEqual(escalate(self.policy, 1), "retry")
        self.assertEqual(escalate(self.policy, 3), "notify_team")


if __name__ == "__main__":
    unittest.main()
