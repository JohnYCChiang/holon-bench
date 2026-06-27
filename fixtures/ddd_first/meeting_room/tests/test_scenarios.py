import unittest

from src.meeting_room import Room, TimeSlot


class Booking(unittest.TestCase):
    def test_non_overlapping_bookings_recorded(self):
        room = Room(10)
        room.book(TimeSlot(0, 60), 4)
        room.book(TimeSlot(60, 120), 4)
        self.assertEqual(len(room.bookings), 2)

    def test_overlapping_rejected(self):
        room = Room(10)
        room.book(TimeSlot(0, 60), 4)
        with self.assertRaises(ValueError):
            room.book(TimeSlot(30, 90), 4)


class Slots(unittest.TestCase):
    def test_overlaps_true(self):
        self.assertTrue(TimeSlot(0, 60).overlaps(TimeSlot(30, 90)))

    def test_overlaps_false(self):
        self.assertFalse(TimeSlot(0, 60).overlaps(TimeSlot(60, 120)))


if __name__ == "__main__":
    unittest.main()
