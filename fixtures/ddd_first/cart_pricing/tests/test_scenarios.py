import unittest

from src.cart import Cart, Discount


class Pricing(unittest.TestCase):
    def test_subtotal_sums_items(self):
        cart = Cart("USD")
        cart.add_item("a", 1000, 2)
        cart.add_item("b", 500, 1)
        self.assertEqual(cart.subtotal(), 2500)

    def test_discount_applied_to_total(self):
        cart = Cart("USD")
        cart.add_item("a", 1000, 2)
        cart.apply_discount(Discount(10))
        self.assertEqual(cart.total(), 1800)


class RejectedCommands(unittest.TestCase):
    def test_non_positive_quantity_rejected(self):
        cart = Cart("USD")
        with self.assertRaises(ValueError):
            cart.add_item("a", 1000, 0)


if __name__ == "__main__":
    unittest.main()
