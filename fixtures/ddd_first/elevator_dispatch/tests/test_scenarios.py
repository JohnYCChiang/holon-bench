import unittest

from src.elevator import Elevator


class Dispatch(unittest.TestCase):
    def test_serves_requests_in_look_order(self):
        car = Elevator(floors=10)
        car.current = 3
        car.request(5)
        car.request(1)
        car.request(4)
        self.assertEqual(car.run(), [4, 5, 1])
        self.assertEqual(car.pending(), [])

    def test_out_of_range_request_rejected(self):
        car = Elevator(floors=5)
        with self.assertRaises(ValueError):
            car.request(9)


if __name__ == "__main__":
    unittest.main()
