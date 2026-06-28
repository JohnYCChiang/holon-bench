import unittest

from src.ansi_tool.strip import strip_ansi


class AnsiStripTest(unittest.TestCase):
    def test_strips_color_codes(self):
        r = strip_ansi("\x1b[31mred\x1b[0m")
        self.assertTrue(r["ok"])
        self.assertEqual(r["clean"], "red")
        self.assertEqual(r["stripped"], 2)
        self.assertEqual(r["length"], 3)

    def test_plain_text_unchanged(self):
        r = strip_ansi("hello")
        self.assertEqual(r["clean"], "hello")
        self.assertEqual(r["stripped"], 0)


if __name__ == "__main__":
    unittest.main()
