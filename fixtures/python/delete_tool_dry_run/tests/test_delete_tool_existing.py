import tempfile
import unittest
from pathlib import Path

from src.delete_tool.delete import delete_paths


class DeleteToolExistingTest(unittest.TestCase):
    def test_deletes_existing_file_and_writes_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("a")
            result = delete_paths(tmp, ["a.txt"])

            self.assertEqual(result, {"ok": True, "deleted": ["a.txt"]})
            self.assertFalse((root / "a.txt").exists())
            self.assertEqual((root / ".holon" / "cache" / "delete.log").read_text(), "a.txt")


if __name__ == "__main__":
    unittest.main()
