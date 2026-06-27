import unittest

from src.recipe import Recipe, BatchPlan


class Recipes(unittest.TestCase):
    def test_scale_up(self):
        r = Recipe(2, (("flour", 200), ("egg", 2)))
        doubled = r.scale_to(4)
        self.assertEqual(doubled.servings, 4)
        self.assertEqual(doubled.ingredients, (("flour", 400), ("egg", 4)))

    def test_fractional_scale_rejected(self):
        r = Recipe(2, (("egg", 1),))
        with self.assertRaises(ValueError):
            r.scale_to(3)


if __name__ == "__main__":
    unittest.main()
