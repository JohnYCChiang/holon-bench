import unittest

from engine import category_of, load_taxonomy


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.tax = load_taxonomy()

    def test_regression_is_bug(self):
        self.assertEqual(category_of(self.tax, "regression"), "bug")

    def test_existing_unchanged(self):
        self.assertEqual(category_of(self.tax, "enhancement"), "feature")


if __name__ == "__main__":
    unittest.main()
