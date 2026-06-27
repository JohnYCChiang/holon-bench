import unittest

from engine import load_sunset, status

TODAY = "2026-06-27"


class SunsetTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_sunset()

    def test_v1_deprecated_now(self):
        self.assertEqual(status(self.cfg, "v1", TODAY), "deprecated")

    def test_v0_already_removed(self):
        self.assertEqual(status(self.cfg, "v0", TODAY), "removed")


if __name__ == "__main__":
    unittest.main()
