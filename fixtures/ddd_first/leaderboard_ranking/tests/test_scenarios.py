import unittest

from src.leaderboard import Leaderboard


class Ranking(unittest.TestCase):
    def test_distinct_scores(self):
        lb = Leaderboard()
        lb.submit("a", 30)
        lb.submit("b", 20)
        lb.submit("c", 10)
        self.assertEqual(lb.ranked(), [(1, "a", 30), (2, "b", 20), (3, "c", 10)])

    def test_duplicate_player_rejected(self):
        lb = Leaderboard()
        lb.submit("a", 30)
        with self.assertRaises(ValueError):
            lb.submit("a", 40)


if __name__ == "__main__":
    unittest.main()
