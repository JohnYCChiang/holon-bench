import unittest

from src.review import review_change


class ReviewPublicTests(unittest.TestCase):
    def test_negative_amount_warns(self):
        self.assertIn("negative amount", review_change({"amount": -1}))


if __name__ == "__main__":
    unittest.main()
