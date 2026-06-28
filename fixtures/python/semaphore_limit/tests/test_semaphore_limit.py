import unittest

from src.semaphore_tool.limit import run_semaphore


class SemaphoreTest(unittest.TestCase):
    def test_rejects_over_capacity(self):
        r = run_semaphore(2, [("acquire", "a"), ("acquire", "b"), ("acquire", "c")])
        self.assertTrue(r["ok"])
        self.assertEqual(r["results"][2]["status"], "rejected")
        self.assertEqual(r["results"][2]["reason"], "at_capacity")
        self.assertEqual(r["peak"], 2)

    def test_release_frees_slot(self):
        r = run_semaphore(2, [("acquire", "a"), ("acquire", "b"), ("release", "a"), ("acquire", "c")])
        self.assertEqual(r["results"][3]["status"], "granted")
        self.assertEqual(r["active"], ["b", "c"])

    def test_invalid_capacity(self):
        r = run_semaphore(0, [])
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_capacity")


if __name__ == "__main__":
    unittest.main()
