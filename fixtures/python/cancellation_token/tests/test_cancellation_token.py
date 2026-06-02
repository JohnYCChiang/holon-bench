import unittest

from src.cancel_tool.processor import CancellationToken, process_batch


class CancellationTokenTest(unittest.TestCase):
    def test_stops_between_items_and_preserves_completed_results(self):
        token = CancellationToken()

        def worker(item):
            if item == 2:
                token.cancel()
            return item * 10

        result = process_batch([1, 2, 3, 4], worker, token)
        self.assertEqual(result["results"], [10, 20])
        self.assertEqual(result["processed"], 2)
        self.assertTrue(result["cancelled"])
        self.assertFalse(result["ok"])

    def test_reports_uncancelled_completion(self):
        token = CancellationToken()
        result = process_batch([1, 2], lambda item: item + 1, token)
        self.assertEqual(result, {"ok": True, "cancelled": False, "results": [2, 3], "processed": 2})


if __name__ == "__main__":
    unittest.main()
