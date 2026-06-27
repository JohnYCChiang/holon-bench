import unittest

from src.warehouse import Warehouse


class Warehousing(unittest.TestCase):
    def test_receive_and_transfer(self):
        wh = Warehouse()
        wh.add_bin("A", 100)
        wh.add_bin("B", 100)
        wh.receive("A", 60)
        wh.transfer("A", "B", 40)
        self.assertEqual(wh.quantity("A"), 20)
        self.assertEqual(wh.quantity("B"), 40)
        self.assertEqual(wh.total_stock(), 60)

    def test_transfer_beyond_stock_rejected(self):
        wh = Warehouse()
        wh.add_bin("A", 100)
        wh.add_bin("B", 100)
        wh.receive("A", 10)
        with self.assertRaises(ValueError):
            wh.transfer("A", "B", 50)


if __name__ == "__main__":
    unittest.main()
