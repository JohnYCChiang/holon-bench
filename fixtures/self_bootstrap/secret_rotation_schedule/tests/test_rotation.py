import unittest

from engine import is_expired, load_json


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_json("rotation.json")
        self.run = load_json("failed_run.json")

    def test_recorded_audit_not_flagged(self):
        self.assertFalse(is_expired(self.cfg, self.run["secret"], self.run["audited_on"]))

    def test_stale_secret_still_expires(self):
        self.assertTrue(is_expired(self.cfg, "db_password", "2030-01-01"))


if __name__ == "__main__":
    unittest.main()
