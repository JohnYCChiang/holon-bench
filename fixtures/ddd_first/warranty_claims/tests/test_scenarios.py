import unittest

from src.warranty import Warranty


class Warranties(unittest.TestCase):
    def test_claim_within_term_approved(self):
        w = Warranty(purchase_day=0, term_days=365, max_claims=3)
        w.file_claim(30, 100)
        self.assertEqual(w.claims_used(), 1)
        self.assertEqual(w.total_claimed(), 100)

    def test_expired_claim_rejected(self):
        w = Warranty(purchase_day=0, term_days=365, max_claims=3)
        with self.assertRaises(ValueError):
            w.file_claim(400, 100)


if __name__ == "__main__":
    unittest.main()
