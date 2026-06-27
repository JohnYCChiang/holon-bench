import unittest

from src.traffic import TrafficLight


class Cycle(unittest.TestCase):
    def test_advance_to_next(self):
        light = TrafficLight("GREEN")
        light.advance()
        self.assertEqual(light.current, "YELLOW")

    def test_full_cycle_events(self):
        light = TrafficLight("GREEN")
        for _ in range(3):
            light.advance()
        self.assertEqual(light.events, ["YELLOW", "RED", "GREEN"])

    def test_invalid_start_rejected(self):
        with self.assertRaises(ValueError):
            TrafficLight("PURPLE")


if __name__ == "__main__":
    unittest.main()
