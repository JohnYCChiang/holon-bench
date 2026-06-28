import unittest

from src.cleanup_tool.registry import CleanupRegistry


class CleanupTest(unittest.TestCase):
    def test_lifo_order(self):
        order = []
        reg = CleanupRegistry()
        for name in ("a", "b", "c"):
            reg.register(name, lambda n=name: order.append(n))
        r = reg.run_all()
        self.assertTrue(r["ok"])
        self.assertEqual(r["ran"], ["c", "b", "a"])
        self.assertEqual(order, ["c", "b", "a"])

    def test_idempotent(self):
        reg = CleanupRegistry()
        reg.register("a", lambda: None)
        reg.run_all()
        second = reg.run_all()
        self.assertEqual(second["ran"], [])


if __name__ == "__main__":
    unittest.main()
