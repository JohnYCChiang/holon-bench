import tempfile
import unittest
from pathlib import Path

from src.file_scanner.scanner import scan_files


class ExistingScannerTest(unittest.TestCase):
    def test_returns_sorted_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "b.txt").write_text("b")
            (root / "a.txt").write_text("a")
            self.assertEqual(scan_files(tmp)["files"], ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
