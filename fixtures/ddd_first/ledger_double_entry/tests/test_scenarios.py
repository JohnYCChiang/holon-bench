import unittest

from src.ledger import Ledger


class Posting(unittest.TestCase):
    def test_balanced_posting_updates_accounts(self):
        ledger = Ledger()
        ledger.post([("cash", 100), ("revenue", -100)])
        self.assertEqual(ledger.balance("cash"), 100)
        self.assertEqual(ledger.balance("revenue"), -100)

    def test_unbalanced_posting_rejected(self):
        ledger = Ledger()
        with self.assertRaises(ValueError):
            ledger.post([("cash", 100), ("revenue", -50)])


if __name__ == "__main__":
    unittest.main()
