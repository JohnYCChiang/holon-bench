import os
import tempfile
import unittest

from src.logrotate_tool.rotate import rotate


class LogRotationTest(unittest.TestCase):
    def test_under_threshold_no_rotation(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "app.log")
            with open(path, "w") as handle:
                handle.write("small")
            r = rotate(path, max_bytes=100, backups=3)
            self.assertTrue(r["ok"])
            self.assertFalse(r["rotated"])
            self.assertTrue(os.path.exists(path))
            self.assertFalse(os.path.exists(path + ".1"))

    def test_rotation_creates_backup_and_fresh_file(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "app.log")
            with open(path, "w") as handle:
                handle.write("0123456789")
            r = rotate(path, max_bytes=5, backups=3)
            self.assertTrue(r["rotated"])
            self.assertTrue(os.path.exists(path + ".1"))
            with open(path + ".1") as handle:
                self.assertEqual(handle.read(), "0123456789")
            self.assertEqual(os.path.getsize(path), 0)


if __name__ == "__main__":
    unittest.main()
