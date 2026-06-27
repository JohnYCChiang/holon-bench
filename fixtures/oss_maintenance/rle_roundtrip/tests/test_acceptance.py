import unittest

from src.rle import encode, decode


class AcceptanceTests(unittest.TestCase):
    def test_roundtrip_multidigit_run(self):
        original = "a" * 12
        self.assertEqual(encode(original), "a12")
        self.assertEqual(decode(encode(original)), original)


if __name__ == "__main__":
    unittest.main()
