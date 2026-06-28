import unittest

from src.debounce_tool.debounce import debounce


class DebounceTest(unittest.TestCase):
    def test_single_burst_emits_last(self):
        r = debounce([{"id": "a", "ts": 0}, {"id": "b", "ts": 10}, {"id": "c", "ts": 20}], 15)
        self.assertTrue(r["ok"])
        self.assertEqual(r["emitted"], ["c"])
        self.assertEqual(r["bursts"], 1)
        self.assertEqual(r["dropped"], 2)

    def test_two_bursts(self):
        r = debounce([{"id": "a", "ts": 0}, {"id": "b", "ts": 100}], 15)
        self.assertEqual(r["emitted"], ["a", "b"])
        self.assertEqual(r["bursts"], 2)

    def test_invalid_window(self):
        r = debounce([], -1)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_window")


if __name__ == "__main__":
    unittest.main()
