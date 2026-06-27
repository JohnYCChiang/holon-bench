import unittest

from engine import authorize, load_matrix


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.matrix = load_matrix()

    def test_maintainer_can_merge(self):
        # Maintainers now own merges, but the grant is missing.
        self.assertEqual(authorize(self.matrix, "maintainer", "merge_pr"), "allow")

    def test_existing_grant_preserved(self):
        self.assertEqual(authorize(self.matrix, "maintainer", "label"), "allow")


if __name__ == "__main__":
    unittest.main()
