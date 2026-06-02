import tempfile
import unittest
from pathlib import Path

from src.delete_tool.delete import delete_paths


class DeleteToolDryRunTest(unittest.TestCase):
    def test_dry_run_does_not_delete_or_write_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("a")
            result = delete_paths(tmp, ["a.txt"], dry_run=True)

            self.assertTrue((root / "a.txt").exists())
            self.assertFalse((root / ".holon" / "cache").exists())
            self.assertEqual(
                result,
                {
                    "ok": True,
                    "deleted": [],
                    "dry_run_report": {"would_delete": ["a.txt"], "missing": []},
                },
            )

    def test_dry_run_still_rejects_unsafe_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = delete_paths(tmp, ["../escape.txt"], dry_run=True)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsafe_path")


if __name__ == "__main__":
    unittest.main()
