import unittest

from src.report import render_report


class AcceptanceTests(unittest.TestCase):
    """Encodes the reported symptom as the acceptance criterion."""

    def test_multi_digit_severity_orders_numerically(self):
        out = render_report(
            [{"name": "disk", "severity": 9}, {"name": "auth", "severity": 10}]
        )
        self.assertEqual(out, ["10:auth", "9:disk"])


if __name__ == "__main__":
    unittest.main()
