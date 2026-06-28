import unittest

from src.residency import residency_endpoint


class ResidencyPublicTests(unittest.TestCase):
    def test_residency_endpoint_is_string(self):
        self.assertIsInstance(residency_endpoint(), str)


if __name__ == "__main__":
    unittest.main()
