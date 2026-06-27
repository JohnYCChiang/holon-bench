import unittest

from src.textutil import truncate_utf8


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_multibyte_boundary_does_not_crash(self):
        self.assertEqual(truncate_utf8("héllo", 2), "h")


if __name__ == "__main__":
    unittest.main()
