import unittest

from src.tarsafe_tool.check import check_member


class TarSafeTest(unittest.TestCase):
    def test_parent_traversal(self):
        r = check_member("../etc")
        self.assertTrue(r["ok"])
        self.assertFalse(r["safe"])
        self.assertEqual(r["reason"], "parent_traversal")

    def test_absolute_path(self):
        r = check_member("/etc/passwd")
        self.assertFalse(r["safe"])
        self.assertEqual(r["reason"], "absolute_path")

    def test_safe_member(self):
        r = check_member("sub/file.txt")
        self.assertTrue(r["safe"])


if __name__ == "__main__":
    unittest.main()
