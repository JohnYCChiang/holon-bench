import unittest

from engine import load_config, redact


class RedactionTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.record = {
            "username": "bob",
            "password": "hunter2",
            "api_key": "AKIA123",
            "ssn": "111-22-3333",
        }

    def test_ssn_is_redacted(self):
        self.assertEqual(redact(self.config, self.record)["ssn"], "***")

    def test_username_stays_visible(self):
        self.assertEqual(redact(self.config, self.record)["username"], "bob")


if __name__ == "__main__":
    unittest.main()
