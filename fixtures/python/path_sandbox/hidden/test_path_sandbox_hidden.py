import tempfile
import unittest
from pathlib import Path

from src.path_sandbox.resolver import resolve_workspace_path


class HiddenPathSandboxTest(unittest.TestCase):
    def test_rejects_absolute_path_outside_workspace_with_structured_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()

            result = resolve_workspace_path(root, str(outside / "secret.txt"))

            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "unsafe_path")

    def test_rejects_resolved_sibling_prefix_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            sibling = Path(tmp) / "repo_evil"
            root.mkdir()
            sibling.mkdir()

            result = resolve_workspace_path(root, "../repo_evil/secret.txt")

            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "unsafe_path")


if __name__ == "__main__":
    unittest.main()
