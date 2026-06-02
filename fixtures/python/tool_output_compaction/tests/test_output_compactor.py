import unittest

from src.output_compactor.compactor import compact_output


class OutputCompactorTest(unittest.TestCase):
    def test_short_output_is_unchanged(self):
        result = {"ok": True, "status": "done", "output": "short"}
        self.assertEqual(compact_output(result, 20), result)

    def test_long_output_keeps_machine_fields_and_debug_tail(self):
        result = {"ok": True, "status": "done", "trace_id": "abc", "output": "0123456789abcdef"}
        compacted = compact_output(result, 8)

        self.assertTrue(compacted["ok"])
        self.assertEqual(compacted["status"], "done")
        self.assertEqual(compacted["trace_id"], "abc")
        self.assertEqual(compacted["original_length"], 16)
        self.assertEqual(compacted["omitted_chars"], 8)
        self.assertEqual(compacted["output_tail"], "89abcdef")
        self.assertIn("01234567", compacted["summary"])


if __name__ == "__main__":
    unittest.main()
