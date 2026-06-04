import unittest

from src.retry_tool.retry import ToolFailure, run_with_retry


class RetryTaxonomyMutationTest(unittest.TestCase):
    def test_permanent_failure_is_never_retried(self):
        calls = []

        def permanent():
            calls.append("call")
            raise ToolFailure("permanent")

        result = run_with_retry(permanent, max_attempts=4)

        self.assertEqual(len(calls), 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "permanent")
        self.assertEqual(result["attempts"], 1)
        self.assertFalse(result["retried"])


if __name__ == "__main__":
    unittest.main()
