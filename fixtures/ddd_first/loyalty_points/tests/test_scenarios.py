import unittest

from src.loyalty import LoyaltyAccount


class Loyalty(unittest.TestCase):
    def test_earn_and_redeem(self):
        acct = LoyaltyAccount()
        acct.earn(500)  # 5 points
        self.assertEqual(acct.balance, 5)
        acct.redeem(2)
        self.assertEqual(acct.balance, 3)

    def test_overspend_rejected(self):
        acct = LoyaltyAccount()
        acct.earn(300)
        with self.assertRaises(ValueError):
            acct.redeem(10)


if __name__ == "__main__":
    unittest.main()
