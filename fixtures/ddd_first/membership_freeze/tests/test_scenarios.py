import unittest

from src.membership import Membership


class Freeze(unittest.TestCase):
    def test_freeze_then_unfreeze(self):
        m = Membership()
        m.freeze(2)
        self.assertEqual(m.state, "FROZEN")
        self.assertEqual(m.frozen_used, 2)
        m.unfreeze()
        self.assertEqual(m.state, "ACTIVE")

    def test_freeze_event(self):
        m = Membership()
        m.freeze(1)
        self.assertEqual(m.events, ["Frozen:1"])


if __name__ == "__main__":
    unittest.main()
