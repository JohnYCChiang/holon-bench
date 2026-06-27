import unittest

from src.nutrition import Nutrition, Recipe


class Totals(unittest.TestCase):
    def test_sum_ingredients(self):
        r = Recipe()
        r.add_ingredient("egg", Nutrition(70, 6, 1, 5), 2)
        r.add_ingredient("toast", Nutrition(80, 3, 14, 1), 1)
        self.assertEqual(r.total(), Nutrition(220, 15, 16, 11))

    def test_scale(self):
        self.assertEqual(Nutrition(10, 1, 2, 3).scale(3), Nutrition(30, 3, 6, 9))


if __name__ == "__main__":
    unittest.main()
