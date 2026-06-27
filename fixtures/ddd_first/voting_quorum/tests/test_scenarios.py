import unittest

from src.voting import Poll


class Voting(unittest.TestCase):
    def test_majority_result(self):
        poll = Poll(["a", "b", "c"], ["yes", "no"], quorum=2)
        poll.cast("a", "yes")
        poll.cast("b", "yes")
        poll.cast("c", "no")
        poll.close()
        self.assertEqual(poll.result(), "yes")

    def test_duplicate_vote_rejected(self):
        poll = Poll(["a", "b"], ["yes", "no"], quorum=1)
        poll.cast("a", "yes")
        with self.assertRaises(ValueError):
            poll.cast("a", "no")


if __name__ == "__main__":
    unittest.main()
