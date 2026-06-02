import unittest

from src.golden_harness.compare import compare_json


class GoldenHarnessTest(unittest.TestCase):
    def test_ignores_generated_at_at_any_depth(self):
        actual = '{"status":"ok","generated_at":"now","items":[{"id":1,"generated_at":"later"}]}'
        expected = '{"items":[{"generated_at":"then","id":1}],"status":"ok"}'
        self.assertEqual(compare_json(actual, expected), {"ok": True, "mismatches": []})

    def test_reports_deterministic_mismatch_paths(self):
        actual = '{"a":1,"b":{"c":2},"items":[{"id":1}]}'
        expected = '{"a":9,"b":{"c":3},"items":[{"id":2}]}'
        result = compare_json(actual, expected)
        self.assertFalse(result["ok"])
        self.assertEqual(result["mismatches"], ["$.a", "$.b.c", "$.items[0].id"])


if __name__ == "__main__":
    unittest.main()
