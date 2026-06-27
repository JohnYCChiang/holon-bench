import unittest

from src.sla import SLAMonitor


class SLA(unittest.TestCase):
    def test_breach_after_tolerance(self):
        mon = SLAMonitor(threshold=100, tolerance=3)
        mon.record(150)
        mon.record(150)
        self.assertFalse(mon.is_breached())
        mon.record(150)
        self.assertTrue(mon.is_breached())
        self.assertEqual(mon.breach_count(), 1)

    def test_healthy_reading_resets(self):
        mon = SLAMonitor(threshold=100, tolerance=2)
        mon.record(150)
        mon.record(50)  # healthy reset
        mon.record(150)
        self.assertFalse(mon.is_breached())


if __name__ == "__main__":
    unittest.main()
