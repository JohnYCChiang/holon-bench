import unittest

from src.giftcard import GiftCard


class GiftCards(unittest.TestCase):
    def test_load_then_redeem(self):
        card = GiftCard(max_balance=10000)
        card.load(5000)
        card.redeem(2000)
        self.assertEqual(card.balance, 3000)
        self.assertEqual(card.available(), 7000)

    def test_overdraw_redeem_rejected(self):
        card = GiftCard(max_balance=10000)
        card.load(1000)
        with self.assertRaises(ValueError):
            card.redeem(2000)


if __name__ == "__main__":
    unittest.main()
