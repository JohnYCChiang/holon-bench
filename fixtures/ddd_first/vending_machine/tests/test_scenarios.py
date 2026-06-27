import unittest

from src.vending import VendingMachine


class Dispense(unittest.TestCase):
    def test_greedy_change(self):
        m = VendingMachine({25: 4, 10: 4, 5: 4, 1: 10})
        self.assertEqual(m.dispense_change(30), {25: 1, 5: 1})
        self.assertEqual(m.inventory[25], 3)

    def test_zero_amount(self):
        m = VendingMachine({25: 1})
        self.assertEqual(m.dispense_change(0), {})


if __name__ == "__main__":
    unittest.main()
