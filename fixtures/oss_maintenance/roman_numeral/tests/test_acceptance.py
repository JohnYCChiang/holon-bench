import unittest

from src.roman import roman_to_int


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_subtractive_pair(self):
        self.assertEqual(roman_to_int("IV"), 4)
        self.assertEqual(roman_to_int("IX"), 9)


if __name__ == "__main__":
    unittest.main()
