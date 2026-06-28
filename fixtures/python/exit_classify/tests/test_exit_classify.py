import unittest

from src.exit_tool.classify import classify_exit


class ExitClassifyTest(unittest.TestCase):
    def test_zero_is_success(self):
        self.assertEqual(
            classify_exit(0),
            {"ok": True, "status": "success", "exit_code": 0, "signal": None},
        )

    def test_positive_is_error(self):
        r = classify_exit(1)
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "error")
        self.assertEqual(r["exit_code"], 1)
        self.assertIsNone(r["signal"])

    def test_negative_is_signaled(self):
        r = classify_exit(-9)
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "signaled")
        self.assertEqual(r["signal"], 9)
        self.assertEqual(r["exit_code"], 137)


if __name__ == "__main__":
    unittest.main()
