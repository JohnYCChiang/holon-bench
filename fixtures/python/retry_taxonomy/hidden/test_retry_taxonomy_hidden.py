import unittest

from src.retry_tool.retry import ToolFailure, run_with_retry


class RetryTaxonomyHiddenTest(unittest.TestCase):
    def test_transient_exhaustion_preserves_final_error_and_attempt_metadata(self):
        calls = []

        def transient():
            calls.append("call")
            raise ToolFailure("transient")

        result = run_with_retry(transient, max_attempts=2)

        self.assertEqual(len(calls), 2)
        self.assertEqual(result["error"]["code"], "transient")
        self.assertEqual(result["attempts"], 2)
        self.assertTrue(result["retried"])


if __name__ == "__main__":
    unittest.main()
