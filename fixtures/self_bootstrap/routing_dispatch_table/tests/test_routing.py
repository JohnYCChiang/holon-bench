import unittest

from engine import dispatch, load_routing


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.routing = load_routing()

    def test_migration_task_is_routed(self):
        # schema_migration submissions are silently dropped to the default.
        self.assertEqual(dispatch(self.routing, "schema_migration"), "migration_worker")

    def test_existing_route_preserved(self):
        self.assertEqual(dispatch(self.routing, "lint"), "style_worker")


if __name__ == "__main__":
    unittest.main()
