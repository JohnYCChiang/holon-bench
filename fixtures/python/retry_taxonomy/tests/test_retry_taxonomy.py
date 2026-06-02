import unittest

from src.retry_tool.retry import ToolFailure, run_with_retry


class RetryTaxonomyTest(unittest.TestCase):
    def test_retries_transient_failure_and_records_attempts(self):
        calls = []

        def flaky():
            calls.append("call")
            if len(calls) == 1:
                raise ToolFailure("transient")
            return "ok"

        result = run_with_retry(flaky, max_attempts=3)
        self.assertEqual(result, {"ok": True, "value": "ok", "attempts": 2, "retried": True})

    def test_does_not_retry_validation_error(self):
        calls = []

        def invalid():
            calls.append("call")
            raise ToolFailure("validation")

        result = run_with_retry(invalid, max_attempts=3)
        self.assertEqual(len(calls), 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "validation")
        self.assertEqual(result["attempts"], 1)
        self.assertFalse(result["retried"])


if __name__ == "__main__":
    unittest.main()
