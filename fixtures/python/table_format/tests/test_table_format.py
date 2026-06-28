import unittest

from src.table_tool.format import format_table


class TableFormatTest(unittest.TestCase):
    def test_aligned_columns(self):
        rows = [{"name": "al", "age": "30"}, {"name": "robert", "age": "5"}]
        r = format_table(rows, ["name", "age"])
        self.assertTrue(r["ok"])
        expected = "\n".join([
            "name   | age",
            "-------+----",
            "al     | 30 ",
            "robert | 5  ",
        ])
        self.assertEqual(r["text"], expected)
        self.assertEqual(r["rows"], 2)
        self.assertEqual(r["columns"], ["name", "age"])


if __name__ == "__main__":
    unittest.main()
