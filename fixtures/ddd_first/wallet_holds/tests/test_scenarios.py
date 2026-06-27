import unittest

from src.wallet import Bank


class Transfer(unittest.TestCase):
    def test_hold_and_capture_moves_funds(self):
        bank = Bank()
        bank.open("A", 100)
        bank.open("B", 0)
        hid = bank.place_hold("A", 40)
        self.assertEqual(bank.available("A"), 60)
        bank.capture(hid, "B")
        self.assertEqual(bank.balances["A"], 60)
        self.assertEqual(bank.balances["B"], 40)
        self.assertEqual(bank.total_balance(), 100)

    def test_hold_beyond_available_rejected(self):
        bank = Bank()
        bank.open("A", 50)
        with self.assertRaises(ValueError):
            bank.place_hold("A", 80)


if __name__ == "__main__":
    unittest.main()
