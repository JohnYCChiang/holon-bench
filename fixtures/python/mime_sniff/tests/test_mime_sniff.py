import unittest

from src.mime_tool.detect import detect


class MimeTest(unittest.TestCase):
    def test_png_magic(self):
        r = detect(b"\x89PNG\r\n\x1a\nrest")
        self.assertTrue(r["ok"])
        self.assertEqual(r["mime"], "image/png")
        self.assertEqual(r["source"], "magic")

    def test_extension_fallback(self):
        r = detect(b"unknownbytes", filename="data.json")
        self.assertEqual(r["mime"], "application/json")
        self.assertEqual(r["source"], "extension")

    def test_default(self):
        r = detect(b"unknownbytes")
        self.assertEqual(r["mime"], "application/octet-stream")
        self.assertEqual(r["source"], "default")


if __name__ == "__main__":
    unittest.main()
