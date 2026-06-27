import unittest

from src.box import ShippingBox


class Packing(unittest.TestCase):
    def test_pack_accumulates_weight(self):
        box = ShippingBox(max_weight=1000, max_items=5)
        box.pack(300)
        box.pack(200)
        self.assertEqual(box.total_weight(), 500)
        self.assertEqual(box.count(), 2)

    def test_overweight_pack_rejected(self):
        box = ShippingBox(max_weight=500, max_items=5)
        box.pack(300)
        with self.assertRaises(ValueError):
            box.pack(300)


if __name__ == "__main__":
    unittest.main()
