import unittest

from src.subscription import Subscription


class Lifecycle(unittest.TestCase):
    def test_trialing_to_active(self):
        sub = Subscription()
        sub.activate()
        self.assertEqual(sub.state, "active")

    def test_active_to_canceled(self):
        sub = Subscription()
        sub.activate()
        sub.cancel()
        self.assertEqual(sub.state, "canceled")


class TerminalState(unittest.TestCase):
    def test_cannot_activate_after_cancel(self):
        sub = Subscription()
        sub.cancel()
        with self.assertRaises(ValueError):
            sub.activate()


if __name__ == "__main__":
    unittest.main()
