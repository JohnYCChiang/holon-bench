import unittest

from src.insurance import InsurancePolicy


class Quote(unittest.TestCase):
    def test_young_driver_surcharge(self):
        p = InsurancePolicy(10000)
        self.assertEqual(p.quote(age=20, prior_claims=0, loyalty_years=0), 15000)

    def test_middle_age_base(self):
        p = InsurancePolicy(10000)
        self.assertEqual(p.quote(age=40, prior_claims=0, loyalty_years=0), 10000)


if __name__ == "__main__":
    unittest.main()
