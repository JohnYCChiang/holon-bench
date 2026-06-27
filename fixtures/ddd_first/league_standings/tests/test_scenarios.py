import unittest

from src.standings import League


class Record(unittest.TestCase):
    def test_win_awards_three_points(self):
        lg = League(["A", "B"])
        lg.record_match("A", "B", 2, 0)
        self.assertEqual(lg.stats["A"]["pts"], 3)
        self.assertEqual(lg.stats["B"]["pts"], 0)

    def test_draw_awards_one_each(self):
        lg = League(["A", "B"])
        lg.record_match("A", "B", 1, 1)
        self.assertEqual(lg.stats["A"]["pts"], 1)
        self.assertEqual(lg.stats["B"]["pts"], 1)


if __name__ == "__main__":
    unittest.main()
