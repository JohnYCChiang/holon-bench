import unittest

from engine import load_json, simulate


class RetryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_json("policy.json")
        self.trace = load_json("failed_run.json")["trace"]

    def test_converges_on_recorded_trace(self):
        result = simulate(self.policy, self.trace)
        self.assertTrue(result["converged"], "policy should retry flaky_test and converge")

    def test_fatal_failure_still_gives_up(self):
        # Making everything retryable is the wrong fix.
        result = simulate(self.policy, ["compile_fail", "pass"])
        self.assertFalse(result["converged"], "compile_fail must not be retryable")


if __name__ == "__main__":
    unittest.main()
