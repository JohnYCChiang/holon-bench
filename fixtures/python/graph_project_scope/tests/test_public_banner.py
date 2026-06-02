import unittest

from src.banner import support_banner


class BannerPublicTests(unittest.TestCase):
    def test_support_banner_is_string(self):
        self.assertIsInstance(support_banner(), str)


if __name__ == "__main__":
    unittest.main()
