import unittest

from src.booking import Calendar, Interval


class Booking(unittest.TestCase):
    def test_non_overlapping_bookings_recorded(self):
        cal = Calendar()
        cal.book(9, 10)
        cal.book(11, 12)
        self.assertEqual(len(cal.reservations), 2)

    def test_overlapping_booking_rejected(self):
        cal = Calendar()
        cal.book(9, 11)
        with self.assertRaises(ValueError):
            cal.book(10, 12)


class Adjacency(unittest.TestCase):
    def test_touching_intervals_do_not_overlap(self):
        self.assertFalse(Interval(10, 12).overlaps(Interval(12, 14)))


if __name__ == "__main__":
    unittest.main()
