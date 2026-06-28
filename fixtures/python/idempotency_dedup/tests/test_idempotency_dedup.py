import unittest

from src.idempotency_tool.dedup import IdempotentRunner


class IdempotencyDedupTest(unittest.TestCase):
    def test_repeat_key_returns_cached_without_rerun(self):
        runner = IdempotentRunner()
        calls = []

        def fn():
            calls.append(1)
            return 42

        a = runner.run("k", fn)
        b = runner.run("k", fn)
        self.assertEqual(a, {"ok": True, "value": 42, "cached": False})
        self.assertEqual(b, {"ok": True, "value": 42, "cached": True})
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
