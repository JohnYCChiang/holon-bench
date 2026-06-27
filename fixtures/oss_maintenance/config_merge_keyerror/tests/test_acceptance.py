import unittest

from src.config import merge_config


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_missing_optional_limits_does_not_crash(self):
        base = {"limits": {"timeout": 30}, "name": "default"}
        override = {"name": "prod"}
        merged = merge_config(base, override)
        self.assertEqual(merged["name"], "prod")
        self.assertEqual(merged["effective_timeout"], 30)


if __name__ == "__main__":
    unittest.main()
