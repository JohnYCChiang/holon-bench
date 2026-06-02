import json
import tempfile
import time
import unittest
from pathlib import Path

from src.cache_tool.cache import write_cache


class IncrementalCacheTest(unittest.TestCase):
    def test_skips_rewrite_when_content_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_cache(tmp, "src/index", {"b": 2, "a": 1})
            path = Path(first["path"])
            before = path.stat().st_mtime_ns
            time.sleep(0.01)

            second = write_cache(tmp, "src/index", {"a": 1, "b": 2})

            self.assertEqual(second["path"], first["path"])
            self.assertFalse(second["written"])
            self.assertEqual(path.stat().st_mtime_ns, before)
            self.assertEqual(json.loads(path.read_text()), {"a": 1, "b": 2})

    def test_reports_written_when_content_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_cache(tmp, "src/index", {"a": 1})
            result = write_cache(tmp, "src/index", {"a": 2})
            self.assertTrue(result["written"])


if __name__ == "__main__":
    unittest.main()
