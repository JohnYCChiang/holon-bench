import unittest

from src.approval import needs_approval


class ApprovalPublicTests(unittest.TestCase):
    def test_returns_bool(self):
        self.assertIsInstance(needs_approval({"amount": 100, "role": "staff"}), bool)

    def test_small_amount_needs_no_approval(self):
        # Small spend is auto-approved regardless of role.
        self.assertFalse(needs_approval({"amount": 100, "role": "staff"}))


if __name__ == "__main__":
    unittest.main()
