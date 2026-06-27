import unittest

from src.hotel import Reservation


class Upgrade(unittest.TestCase):
    def test_upgrade_returns_surcharge(self):
        r = Reservation("STANDARD", 2)
        self.assertEqual(r.upgrade("DELUXE"), 120)
        self.assertEqual(r.room_class, "DELUXE")
        self.assertEqual(r.events, ["Upgraded:DELUXE"])

    def test_downgrade_rejected(self):
        r = Reservation("SUITE", 1)
        with self.assertRaises(ValueError):
            r.upgrade("STANDARD")


if __name__ == "__main__":
    unittest.main()
