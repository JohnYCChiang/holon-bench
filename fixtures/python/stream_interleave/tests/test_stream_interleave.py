import unittest

from src.streammux_tool.interleave import interleave


class StreamInterleaveTest(unittest.TestCase):
    def test_ordered_by_seq(self):
        events = [
            {"stream": "stdout", "seq": 1, "text": "a"},
            {"stream": "stderr", "seq": 2, "text": "b"},
            {"stream": "stdout", "seq": 3, "text": "c"},
        ]
        r = interleave(events)
        self.assertTrue(r["ok"])
        self.assertEqual(
            r["transcript"],
            [
                {"stream": "stdout", "text": "a"},
                {"stream": "stderr", "text": "b"},
                {"stream": "stdout", "text": "c"},
            ],
        )

    def test_byte_counts(self):
        events = [
            {"stream": "stdout", "seq": 1, "text": "ab"},
            {"stream": "stderr", "seq": 2, "text": "ccc"},
        ]
        r = interleave(events)
        self.assertEqual(r["stdout_bytes"], 2)
        self.assertEqual(r["stderr_bytes"], 3)


if __name__ == "__main__":
    unittest.main()
