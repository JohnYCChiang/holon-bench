import unittest

from src.seating import SeatMap


class Seating(unittest.TestCase):
    def test_hold_then_confirm(self):
        hall = SeatMap(seat_count=10)
        hall.hold(3, ttl=5)
        self.assertFalse(hall.is_free(3))
        hall.confirm(3)
        self.assertFalse(hall.is_free(3))

    def test_double_hold_rejected(self):
        hall = SeatMap(seat_count=10)
        hall.hold(3, ttl=5)
        with self.assertRaises(ValueError):
            hall.hold(3, ttl=5)


if __name__ == "__main__":
    unittest.main()
