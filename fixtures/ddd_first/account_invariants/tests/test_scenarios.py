import unittest

from src.account import BankAccount


class DepositThenWithdraw(unittest.TestCase):
    def test_balance_after_flow(self):
        acct = BankAccount(daily_limit=1000)
        acct.deposit(500)
        acct.withdraw(200)
        self.assertEqual(acct.balance, 300)


class Overdraw(unittest.TestCase):
    def test_withdraw_beyond_balance_rejected(self):
        acct = BankAccount(daily_limit=1000)
        acct.deposit(100)
        with self.assertRaises(ValueError):
            acct.withdraw(200)


class DailyLimitAcrossCommands(unittest.TestCase):
    def test_cumulative_withdrawals_cannot_exceed_limit(self):
        acct = BankAccount(daily_limit=300)
        acct.deposit(1000)
        acct.withdraw(200)
        with self.assertRaises(ValueError):
            acct.withdraw(150)  # 200 + 150 > 300, even though balance allows it


if __name__ == "__main__":
    unittest.main()
