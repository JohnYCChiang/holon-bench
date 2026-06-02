import unittest

from src.router import route_key


class RouterPublicTests(unittest.TestCase):
    def test_returns_a_string(self):
        self.assertIsInstance(route_key({"tenant": "acme", "type": "invoice"}), str)


if __name__ == "__main__":
    unittest.main()
