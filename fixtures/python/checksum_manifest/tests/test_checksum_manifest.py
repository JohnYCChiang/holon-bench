import hashlib
import os
import tempfile
import unittest

from src.checksum_tool.manifest import build_manifest


class ChecksumManifestTest(unittest.TestCase):
    def test_lists_files_with_hash_and_size(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "a.txt"), "wb") as handle:
                handle.write(b"hello")
            r = build_manifest(root)
            self.assertTrue(r["ok"])
            self.assertEqual(r["count"], 1)
            entry = r["files"][0]
            self.assertEqual(entry["path"], "a.txt")
            self.assertEqual(entry["size"], 5)
            self.assertEqual(entry["sha256"], hashlib.sha256(b"hello").hexdigest())

    def test_sorted_relative_paths(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("b.txt", "a.txt"):
                with open(os.path.join(root, name), "wb") as handle:
                    handle.write(b"x")
            r = build_manifest(root)
            self.assertEqual([e["path"] for e in r["files"]], ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
