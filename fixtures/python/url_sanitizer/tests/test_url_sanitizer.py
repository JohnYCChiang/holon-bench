import unittest

from src.urlsan_tool.sanitize import sanitize


class UrlSanitizeTest(unittest.TestCase):
    def test_full_normalization(self):
        r = sanitize("HTTP://User:pw@Example.COM:80/Path?b=2&a=1")
        self.assertTrue(r["ok"])
        self.assertEqual(r["url"], "http://example.com/Path?a=1&b=2")
        self.assertTrue(r["removed_credentials"])

    def test_no_credentials_flag(self):
        r = sanitize("http://example.com/p")
        self.assertFalse(r["removed_credentials"])

    def test_bad_scheme(self):
        r = sanitize("ftp://example.com/x")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_scheme")


if __name__ == "__main__":
    unittest.main()
