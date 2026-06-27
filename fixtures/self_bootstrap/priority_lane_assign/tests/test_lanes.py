import unittest

from engine import lane_of, load_lanes, priority


class LaneTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_lanes()

    def test_incident_is_express(self):
        self.assertEqual(lane_of(self.cfg, "incident_response"), "express")

    def test_incident_outranks_cleanup(self):
        self.assertLess(priority(self.cfg, "incident_response"), priority(self.cfg, "cleanup"))


if __name__ == "__main__":
    unittest.main()
