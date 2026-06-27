import unittest

from src.refund import RefundPolicy


class Refund(unittest.TestCase):
    def test_full_refund_minus_fee(self):
        self.assertEqual(RefundPolicy().refund(10000, 10), 9500)

    def test_no_refund_close_to_event(self):
        self.assertEqual(RefundPolicy().refund(10000, 1), 0)


if __name__ == "__main__":
    unittest.main()
