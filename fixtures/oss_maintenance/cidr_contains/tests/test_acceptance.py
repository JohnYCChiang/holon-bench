import unittest

from src.cidr import contains


class AcceptanceTests(unittest.TestCase):
    def test_network_written_with_host_bits(self):
        self.assertTrue(contains("192.168.1.10/24", "192.168.1.200"))


if __name__ == "__main__":
    unittest.main()
