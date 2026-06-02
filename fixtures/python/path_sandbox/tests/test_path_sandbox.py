import tempfile
import unittest
from pathlib import Path

from src.path_sandbox.resolver import resolve_workspace_path


class PathSandboxTest(unittest.TestCase):
    def test_allows_relative_path_inside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            result = resolve_workspace_path(root, "src/tool.py")
            self.assertTrue(result["ok"])
            self.assertEqual(Path(result["path"]), root / "src" / "tool.py")

    def test_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = resolve_workspace_path(tmp, "../secret.txt")
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "unsafe_path")

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "link").symlink_to(outside)
            result = resolve_workspace_path(root, "link/secret.txt")
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "unsafe_path")


if __name__ == "__main__":
    unittest.main()
