import unittest

from src.csvsniff_tool.sniff import sniff


class CsvSniffTest(unittest.TestCase):
    def test_semicolon_with_header(self):
        r = sniff("name;age;city\nbob;30;ny\nsue;25;la")
        self.assertTrue(r["ok"])
        self.assertEqual(r["delimiter"], ";")
        self.assertTrue(r["has_header"])
        self.assertEqual(r["columns"], 3)

    def test_tab_delimited(self):
        r = sniff("a\tb\n1\t2")
        self.assertEqual(r["delimiter"], "\t")

    def test_empty_sample(self):
        r = sniff("   ")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_sample")


if __name__ == "__main__":
    unittest.main()
