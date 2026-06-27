import unittest

from src.inventory import Inventory


class ReservationFlow(unittest.TestCase):
    def test_reserve_reduces_available(self):
        inv = Inventory(available=10, reorder_to=20)
        inv.reserve(3)
        self.assertEqual(inv.available, 7)

    def test_depletion_emits_event_once(self):
        inv = Inventory(available=2, reorder_to=20)
        inv.reserve(2)
        self.assertEqual(inv.events, ["StockDepleted"])


class ReorderPolicy(unittest.TestCase):
    def test_policy_restocks_and_emits_reordered(self):
        inv = Inventory(available=2, reorder_to=20)
        inv.reserve(2)
        inv.apply_reorder_policy()
        self.assertEqual(inv.available, 20)
        self.assertEqual(inv.events, ["StockDepleted", "Reordered"])


if __name__ == "__main__":
    unittest.main()
