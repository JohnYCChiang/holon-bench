import unittest

from engine import classify, load_severity_map


class SeverityTests(unittest.TestCase):
    def setUp(self):
        self.smap = load_severity_map()

    def test_new_failure_mode_blocks(self):
        self.assertEqual(classify(["state_sync_corruption"], self.smap), "block")

    def test_existing_critical_still_blocks(self):
        self.assertEqual(classify(["public_api_break"], self.smap), "block")

    def test_warning_only_allows(self):
        self.assertEqual(classify(["over_refactor"], self.smap), "allow")


if __name__ == "__main__":
    unittest.main()
