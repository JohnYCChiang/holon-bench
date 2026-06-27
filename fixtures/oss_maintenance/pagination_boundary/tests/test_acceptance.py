import unittest

from src.page import paginate


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_first_page_returns_leading_items(self):
        self.assertEqual(paginate(["a", "b", "c", "d", "e"], 2, 1), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
