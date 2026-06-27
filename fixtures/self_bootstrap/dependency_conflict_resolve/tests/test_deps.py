import unittest

from engine import is_consistent, load_deps, satisfies


class DepsTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_deps()

    def test_lockfile_consistent(self):
        self.assertTrue(is_consistent(self.cfg))

    def test_selected_is_available(self):
        sel = self.cfg["selected"]["libcore"]
        self.assertIn(sel, self.cfg["available"]["libcore"])


if __name__ == "__main__":
    unittest.main()
