import unittest

from src.retention import retention_days


class RetentionPublicTests(unittest.TestCase):
    def test_returns_int(self):
        self.assertIsInstance(retention_days({"data_class": "telemetry"}), int)

    def test_unknown_class_uses_default(self):
        # An unrecognized data class keeps the legacy 30-day default.
        self.assertEqual(retention_days({"data_class": "marketing"}), 30)


if __name__ == "__main__":
    unittest.main()
