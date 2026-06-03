import sys
import unittest

from src.shell_runner.runner import run_command


class HiddenShellRunnerContractTest(unittest.TestCase):
    def test_nonzero_exit_preserves_stdout_stderr_and_exit_code(self):
        code = (
            "import sys; "
            "print('out'); "
            "print('err', file=sys.stderr); "
            "sys.exit(7)"
        )
        result = run_command([sys.executable, "-c", code], timeout_seconds=2)

        self.assertEqual(result["stdout"], "out\n")
        self.assertEqual(result["stderr"], "err\n")
        self.assertEqual(result["exit_code"], 7)
        self.assertFalse(result["timed_out"])
        self.assertIsInstance(result["duration_ms"], int)

    def test_timeout_preserves_partial_stderr(self):
        code = "import sys,time; print('before-err', file=sys.stderr, flush=True); time.sleep(2)"
        result = run_command([sys.executable, "-c", code], timeout_seconds=0.2)

        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "before-err\n")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertTrue(result["timed_out"])
        self.assertLess(result["duration_ms"], 1500)


if __name__ == "__main__":
    unittest.main()
