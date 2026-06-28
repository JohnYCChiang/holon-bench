import unittest

from src.sla import sla_minutes


class SlaPublicTests(unittest.TestCase):
    def test_returns_int(self):
        self.assertIsInstance(sla_minutes({"priority": "p2"}), int)

    def test_unknown_priority_uses_default(self):
        # An unrecognized priority keeps the legacy default window.
        self.assertEqual(sla_minutes({"priority": "p9"}), 600)


if __name__ == "__main__":
    unittest.main()
