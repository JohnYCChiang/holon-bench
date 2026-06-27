import unittest

from src.csvparse import parse_csv


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_comma_inside_quotes(self):
        self.assertEqual(parse_csv('a,"b,c",d'), [["a", "b,c", "d"]])


if __name__ == "__main__":
    unittest.main()
