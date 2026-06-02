import unittest

from src.redaction_tool.redact import redact_output


class OutputRedactionTest(unittest.TestCase):
    def test_redacts_secrets_and_preserves_counts(self):
        text = "start\nAPI_KEY=abc123\nbearer token: sk-live-123456\nend"
        result = redact_output(text, preview_lines=4)
        self.assertEqual(result["line_count"], 4)
        self.assertEqual(result["byte_count"], len(text.encode("utf-8")))
        self.assertEqual(result["redaction_count"], 2)
        self.assertNotIn("abc123", result["redacted"])
        self.assertNotIn("sk-live-123456", result["redacted"])
        self.assertIn("[REDACTED]", result["preview"])


if __name__ == "__main__":
    unittest.main()
