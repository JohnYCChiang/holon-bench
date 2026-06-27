import unittest

from src.humanize import humanize


class AcceptanceTests(unittest.TestCase):
    def test_rounding_rolls_over_to_next_unit(self):
        self.assertEqual(humanize(1048555), "1.0 MiB")


if __name__ == "__main__":
    unittest.main()
