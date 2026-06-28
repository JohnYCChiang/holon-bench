import unittest

from src.cron_tool.schedule import next_run


class CronTest(unittest.TestCase):
    def test_step_field(self):
        r = next_run("*/15", "*", "2026-06-28T10:05:00")
        self.assertTrue(r["ok"])
        self.assertEqual(r["next"], "2026-06-28T10:15:00")

    def test_strictly_after(self):
        r = next_run("*", "*", "2026-06-28T10:05:00")
        self.assertEqual(r["next"], "2026-06-28T10:06:00")

    def test_invalid(self):
        r = next_run("zz", "*", "2026-06-28T10:05:00")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_field")


if __name__ == "__main__":
    unittest.main()
