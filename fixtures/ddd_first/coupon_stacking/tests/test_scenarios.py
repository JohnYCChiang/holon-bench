import unittest

from src.coupons import Coupon, Checkout


class Coupons(unittest.TestCase):
    def test_stacked_percent_then_fixed(self):
        cart = Checkout(1000)
        cart.apply(Coupon("SAVE10", "PERCENT", 10, True))
        cart.apply(Coupon("MINUS100", "FIXED", 100, True))
        # 1000 -> 900 -> 800
        self.assertEqual(cart.total(), 800)

    def test_non_stackable_blocks_second(self):
        cart = Checkout(1000)
        cart.apply(Coupon("ONLY", "FIXED", 100, False))
        with self.assertRaises(ValueError):
            cart.apply(Coupon("SAVE10", "PERCENT", 10, True))


if __name__ == "__main__":
    unittest.main()
