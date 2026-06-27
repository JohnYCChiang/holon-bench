import unittest

from engine import load_fallback, resolve_chain


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_fallback()

    def test_chain_reaches_local(self):
        self.assertEqual(resolve_chain(self.cfg), ["gpt-primary", "gpt-mini", "local-llama"])

    def test_no_cycle(self):
        resolve_chain(self.cfg)  # must not raise


if __name__ == "__main__":
    unittest.main()
