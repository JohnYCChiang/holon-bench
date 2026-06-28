import unittest

from src.tempname_tool.name import temp_name


class TempNameTest(unittest.TestCase):
    def test_deterministic(self):
        a = temp_name("run", "abc")
        b = temp_name("run", "abc")
        self.assertTrue(a["ok"])
        self.assertEqual(a["name"], b["name"])

    def test_no_separator_in_name(self):
        r = temp_name("run", "abc")
        self.assertNotIn("/", r["name"])

    def test_reject_prefix_separator(self):
        r = temp_name("a/b", "x")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_prefix")


if __name__ == "__main__":
    unittest.main()
