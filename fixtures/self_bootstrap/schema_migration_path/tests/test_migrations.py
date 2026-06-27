import unittest

from engine import find_path, load_migrations


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.migrations = load_migrations()

    def test_v1_to_v4_reachable(self):
        # There is currently no bridge between the v1->v2 and v3->v4 islands.
        path = find_path(self.migrations, "v1", "v4")
        self.assertIsNotNone(path, "v1 must be migratable to v4")
        self.assertEqual(path[0], "v1")
        self.assertEqual(path[-1], "v4")

    def test_single_step_preserved(self):
        self.assertEqual(find_path(self.migrations, "v1", "v2"), ["v1", "v2"])


if __name__ == "__main__":
    unittest.main()
