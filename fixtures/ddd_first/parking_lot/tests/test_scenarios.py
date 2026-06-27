import unittest

from src.parking import ParkingLot


class Parking(unittest.TestCase):
    def test_park_and_occupancy(self):
        lot = ParkingLot(small_slots=2, large_slots=1)
        lot.park("AAA", "small")
        lot.park("BBB", "large")
        self.assertEqual(lot.occupancy(), 2)
        self.assertEqual(lot.available_small(), 1)
        self.assertEqual(lot.available_large(), 0)

    def test_park_when_full_rejected(self):
        lot = ParkingLot(small_slots=1, large_slots=1)
        lot.park("AAA", "large")
        with self.assertRaises(ValueError):
            lot.park("BBB", "large")


if __name__ == "__main__":
    unittest.main()
