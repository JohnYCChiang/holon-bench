import unittest

from src.tax import TaxSchedule, TaxReturn


class Taxes(unittest.TestCase):
    def test_progressive_tax(self):
        sched = TaxSchedule(((1000, 0), (5000, 10), (None, 20)))
        # 0..1000:0  1000..5000:4000*10%=400  5000..6000:1000*20%=200
        self.assertEqual(sched.tax_for(6000), 600)

    def test_invalid_schedule_rejected(self):
        with self.assertRaises(ValueError):
            TaxSchedule(((5000, 10), (1000, 20)))  # not ascending


if __name__ == "__main__":
    unittest.main()
