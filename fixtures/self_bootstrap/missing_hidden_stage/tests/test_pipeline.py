import unittest

from engine import evaluate, load_workflow

FULL = {
    "compiles": True,
    "tests_pass": True,
    "scope_pass": True,
    "hidden_pass": True,
    "mutation_pass": True,
}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.wf = load_workflow()

    def test_good_submission_accepted(self):
        self.assertEqual(evaluate(self.wf, FULL), "accept")

    def test_hidden_regression_rejected(self):
        # Passes the visible suite but fails the hidden regression suite.
        bad = {**FULL, "hidden_pass": False}
        self.assertEqual(evaluate(self.wf, bad), "reject")


if __name__ == "__main__":
    unittest.main()
