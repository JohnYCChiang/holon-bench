import unittest

from src.scheduler_tool.scheduler import resolve_order


class DepSchedulerTest(unittest.TestCase):
    def test_dependency_before_dependent(self):
        r = resolve_order({"a": ["z"], "z": []})
        self.assertTrue(r["ok"])
        self.assertEqual(r["order"], ["z", "a"])

    def test_cycle_is_error(self):
        r = resolve_order({"a": ["b"], "b": ["a"]})
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "cycle")

    def test_independent_tasks_sorted(self):
        r = resolve_order({"m": [], "k": []})
        self.assertEqual(r["order"], ["k", "m"])


if __name__ == "__main__":
    unittest.main()
