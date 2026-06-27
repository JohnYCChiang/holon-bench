import unittest

from engine import access, load_mounts


class MountTests(unittest.TestCase):
    def setUp(self):
        self.mounts = load_mounts()

    def test_cache_readable(self):
        self.assertEqual(access(self.mounts, "sandbox", "/data/cache/blob"), "read")

    def test_etc_denied(self):
        self.assertEqual(access(self.mounts, "sandbox", "/etc/passwd"), "none")


if __name__ == "__main__":
    unittest.main()
