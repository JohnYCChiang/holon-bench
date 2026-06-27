import unittest

from src.approval import ApprovalChain


class Flow(unittest.TestCase):
    def test_in_order_approval_completes(self):
        c = ApprovalChain(["alice", "bob"])
        c.approve("alice")
        c.approve("bob")
        self.assertEqual(c.state, "APPROVED")
        self.assertEqual(c.events, ["Approved:alice", "Approved:bob", "DocumentApproved"])

    def test_out_of_order_rejected(self):
        c = ApprovalChain(["alice", "bob"])
        with self.assertRaises(ValueError):
            c.approve("bob")


if __name__ == "__main__":
    unittest.main()
