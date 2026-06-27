import unittest

from src.auction import Auction


class Auctions(unittest.TestCase):
    def test_ascending_bids(self):
        a = Auction(start_price=100, min_increment=10)
        a.bid("alice", 100)
        a.bid("bob", 110)
        self.assertEqual(a.highest_bidder, "bob")
        self.assertEqual(a.highest_bid, 110)

    def test_too_low_bid_rejected(self):
        a = Auction(start_price=100, min_increment=10)
        a.bid("alice", 100)
        with self.assertRaises(ValueError):
            a.bid("bob", 105)


if __name__ == "__main__":
    unittest.main()
