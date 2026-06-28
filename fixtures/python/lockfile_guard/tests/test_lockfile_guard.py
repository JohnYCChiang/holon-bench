import os
import tempfile
import unittest

from src.lock_tool.lock import run_locked


class LockfileGuardTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.lock = os.path.join(self.dir, "x.lock")

    def test_runs_and_releases(self):
        r = run_locked(self.lock, lambda: 7)
        self.assertEqual(r, {"ok": True, "value": 7})
        self.assertFalse(os.path.exists(self.lock))

    def test_rejects_when_held(self):
        with open(self.lock, "w") as handle:
            handle.write("999")
        r = run_locked(self.lock, lambda: 1)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "locked")

    def test_releases_on_exception(self):
        def boom():
            raise RuntimeError("fail")

        with self.assertRaises(RuntimeError):
            run_locked(self.lock, boom)
        self.assertFalse(os.path.exists(self.lock))


if __name__ == "__main__":
    unittest.main()
