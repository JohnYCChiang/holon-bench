import sys
import unittest

from src.shell_runner.runner import run_command


class ShellRunnerTimeoutTest(unittest.TestCase):
    def test_success_preserves_output_shape(self):
        result = run_command([sys.executable, "-c", "print('ok')"], timeout_seconds=2)
        self.assertEqual(result["stdout"], "ok\n")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["timed_out"])
        self.assertIsInstance(result["duration_ms"], int)

    def test_timeout_kills_child_and_keeps_partial_output(self):
        code = "import sys,time; print('before', flush=True); time.sleep(2)"
        result = run_command([sys.executable, "-c", code], timeout_seconds=0.2)
        self.assertEqual(result["stdout"], "before\n")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertTrue(result["timed_out"])
        self.assertLess(result["duration_ms"], 1500)


if __name__ == "__main__":
    unittest.main()
