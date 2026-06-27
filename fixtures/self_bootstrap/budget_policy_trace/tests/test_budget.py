import unittest

from engine import load_json, run_plan


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.budget = load_json("budget.json")
        self.tasks = load_json("failed_run.json")["tasks"]

    def test_recorded_plan_completes(self):
        result = run_plan(self.budget, self.tasks)
        self.assertTrue(result["completed"], "the recorded plan must fit within budget")

    def test_runaway_plan_still_blocked(self):
        # Removing the ceiling is the wrong fix.
        result = run_plan(self.budget, ["patch"] * 50)
        self.assertFalse(result["completed"], "a runaway plan must still exhaust the budget")


if __name__ == "__main__":
    unittest.main()
