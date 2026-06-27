import unittest

from src.seatmap import SeatMap


class Assign(unittest.TestCase):
    def test_assign_and_taken(self):
        m = SeatMap(2, 4)
        m.assign("alice", (1, 1))
        self.assertEqual(m.assignments[(1, 1)], "alice")
        with self.assertRaises(ValueError):
            m.assign("bob", (1, 1))

    def test_group_adjacent(self):
        m = SeatMap(2, 4)
        m.assign_group(["a", "b", "c"], 1)
        self.assertEqual(m.passenger_seat["a"], (1, 1))
        self.assertEqual(m.passenger_seat["c"], (1, 3))
        self.assertIn("GroupAssigned:1:1:3", m.events)


if __name__ == "__main__":
    unittest.main()
