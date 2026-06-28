import unittest

from src.jsonl_tool.stream import parse_jsonl


class JsonlStreamTest(unittest.TestCase):
    def test_parses_records_in_order(self):
        r = parse_jsonl('{"a": 1}\n{"a": 2}')
        self.assertTrue(r["ok"])
        self.assertEqual(r["records"], [{"a": 1}, {"a": 2}])
        self.assertEqual(r["count"], 2)

    def test_trailing_blank_line_ignored(self):
        r = parse_jsonl('{"a": 1}\n')
        self.assertEqual(r["count"], 1)

    def test_malformed_line_is_error(self):
        r = parse_jsonl('{"a": 1}\nnope')
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_jsonl")
        self.assertEqual(r["error"]["line"], 2)


if __name__ == "__main__":
    unittest.main()
