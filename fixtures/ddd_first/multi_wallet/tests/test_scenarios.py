import unittest

from src.wallet import Wallet


class Balances(unittest.TestCase):
    def test_independent_currencies(self):
        w = Wallet()
        w.deposit("USD", 100)
        w.deposit("EUR", 40)
        self.assertEqual(w.balance("USD"), 100)
        self.assertEqual(w.balance("EUR"), 40)

    def test_withdraw_reduces(self):
        w = Wallet()
        w.deposit("USD", 100)
        w.withdraw("USD", 30)
        self.assertEqual(w.balance("USD"), 70)


if __name__ == "__main__":
    unittest.main()
