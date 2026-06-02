import tempfile
import unittest
from pathlib import Path

from src.file_scanner.scanner import scan_files


class ScannerExcludesTest(unittest.TestCase):
    def test_skips_hidden_ignored_binary_and_large_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "visible.txt").write_text("ok")
            (root / ".hidden").mkdir()
            (root / ".hidden" / "secret.txt").write_text("secret")
            (root / "ignored.log").write_text("ignored")
            (root / "binary.bin").write_bytes(b"\x00\x01\x02")
            (root / "large.txt").write_text("x" * 20)

            result = scan_files(tmp, exclude_globs=["*.log"], max_bytes=8)

        self.assertEqual(result["files"], ["visible.txt"])
        self.assertEqual(result["skipped"]["hidden"], 1)
        self.assertEqual(result["skipped"]["ignored"], 1)
        self.assertEqual(result["skipped"]["binary"], 1)
        self.assertEqual(result["skipped"]["too_large"], 1)


if __name__ == "__main__":
    unittest.main()
