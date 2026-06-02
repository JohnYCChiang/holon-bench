import unittest

from src.tool_errors.runner import run_tool


class ToolErrorsTest(unittest.TestCase):
    def test_success_shape_is_preserved(self):
        self.assertEqual(run_tool({"path": "src"}), {"ok": True, "path": "src", "indexed": 1})

    def test_missing_path_has_machine_readable_error(self):
        result = run_tool({})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "missing_path")
        self.assertEqual(result["error"]["message"], "missing path")

    def test_empty_path_has_machine_readable_error(self):
        result = run_tool({"path": ""})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "empty_path")
        self.assertEqual(result["error"]["message"], "empty path")


if __name__ == "__main__":
    unittest.main()
