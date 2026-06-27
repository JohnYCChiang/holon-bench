import unittest

from src.library import Library


class Loans(unittest.TestCase):
    def test_borrow_increments_count(self):
        lib = Library(max_loans=3)
        lib.add_copy("c1")
        lib.borrow("alice", "c1")
        self.assertEqual(lib.loans_of("alice"), 1)
        self.assertFalse(lib.is_available("c1"))

    def test_borrow_over_limit_rejected(self):
        lib = Library(max_loans=1)
        lib.add_copy("c1")
        lib.add_copy("c2")
        lib.borrow("alice", "c1")
        with self.assertRaises(ValueError):
            lib.borrow("alice", "c2")


if __name__ == "__main__":
    unittest.main()
