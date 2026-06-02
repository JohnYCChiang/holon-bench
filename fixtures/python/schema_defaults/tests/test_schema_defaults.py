import unittest

from src.schema_tool.normalize import normalize_request


class SchemaDefaultsTest(unittest.TestCase):
    def test_adds_defaults_without_mutating_input(self):
        payload = {"path": "src"}
        result = normalize_request(payload)
        self.assertEqual(payload, {"path": "src"})
        self.assertEqual(
            result,
            {"ok": True, "request": {"path": "src", "dry_run": False, "limit": 100}},
        )

    def test_preserves_explicit_values(self):
        result = normalize_request({"path": "src", "dry_run": True, "limit": 5})
        self.assertEqual(result["request"]["dry_run"], True)
        self.assertEqual(result["request"]["limit"], 5)

    def test_rejects_unknown_keys(self):
        result = normalize_request({"path": "src", "mode": "fast"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unknown_key")
        self.assertEqual(result["error"]["field"], "mode")


if __name__ == "__main__":
    unittest.main()
