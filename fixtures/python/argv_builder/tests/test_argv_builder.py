import unittest

from src.argv_tool.build import build_argv


class ArgvBuilderTest(unittest.TestCase):
    def test_builds_argv_list_without_shell(self):
        r = build_argv("ls", ["-la", "my dir"])
        self.assertTrue(r["ok"])
        self.assertEqual(r["argv"], ["ls", "-la", "my dir"])
        self.assertFalse(r["shell"])

    def test_injection_arg_stays_single_element(self):
        r = build_argv("echo", ["; rm -rf /"])
        self.assertTrue(r["ok"])
        self.assertEqual(r["argv"], ["echo", "; rm -rf /"])

    def test_empty_program_is_structured_error(self):
        r = build_argv("", ["x"])
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "empty_program")


if __name__ == "__main__":
    unittest.main()
