import tempfile
import unittest
from pathlib import Path

from src.delete_tool.delete import delete_paths


class HiddenDeleteToolDryRunTest(unittest.TestCase):
    def test_dry_run_reports_nested_and_missing_without_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested").mkdir()
            (root / "nested" / "a.txt").write_text("a")
            (root / "b.txt").write_text("b")

            first = delete_paths(
                tmp,
                ["nested/a.txt", "missing.txt", "b.txt"],
                dry_run=True,
            )
            second = delete_paths(
                tmp,
                ["nested/a.txt", "missing.txt", "b.txt"],
                dry_run=True,
            )

            self.assertTrue((root / "nested" / "a.txt").exists())
            self.assertTrue((root / "b.txt").exists())
            self.assertFalse((root / ".holon" / "cache").exists())
            self.assertEqual(first, second)
            self.assertEqual(
                first,
                {
                    "ok": True,
                    "deleted": [],
                    "dry_run_report": {
                        "would_delete": ["nested/a.txt", "b.txt"],
                        "missing": ["missing.txt"],
                    },
                },
            )

    def test_real_delete_writes_cache_but_does_not_report_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("a")
            (root / "b.txt").write_text("b")

            result = delete_paths(tmp, ["a.txt", "missing.txt", "b.txt"], dry_run=False)

            self.assertEqual(result, {"ok": True, "deleted": ["a.txt", "b.txt"]})
            self.assertFalse((root / "a.txt").exists())
            self.assertFalse((root / "b.txt").exists())
            self.assertEqual((root / ".holon" / "cache" / "delete.log").read_text(), "a.txt\nb.txt")
            self.assertNotIn("dry_run_report", result)


if __name__ == "__main__":
    unittest.main()
