import unittest

from src.escalation import escalate


class EscalationPublicTests(unittest.TestCase):
    def test_returns_str(self):
        self.assertIsInstance(escalate({"severity": 3, "environment": "production"}), str)

    def test_low_severity_uses_default_queue(self):
        # Non-critical incidents stay on the default queue.
        self.assertEqual(escalate({"severity": 3, "environment": "production"}), "page:default-queue")


if __name__ == "__main__":
    unittest.main()
