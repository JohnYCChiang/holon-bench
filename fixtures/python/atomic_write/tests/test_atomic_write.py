import tempfile
import unittest
from pathlib import Path

from src.atomic_writer.write import write_text_atomic


class AtomicWriteTest(unittest.TestCase):
    def test_writes_content_and_creates_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "out.txt"
            result = write_text_atomic(target, "hello")
            self.assertTrue(result["ok"])
            self.assertEqual(target.read_text(), "hello")
            self.assertEqual(result["bytes"], 5)

    def test_failure_preserves_existing_destination_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            target.write_text("old", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                write_text_atomic(target, "new", fail_after_temp=True)
            self.assertEqual(target.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
