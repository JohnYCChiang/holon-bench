import unittest

from engine import load_pipeline, resolve_order


class StageOrderTests(unittest.TestCase):
    def setUp(self):
        self.order = resolve_order(load_pipeline())

    def test_integration_runs_before_deploy(self):
        # deploy must never precede integration_test.
        self.assertLess(self.order.index("integration_test"), self.order.index("deploy"))

    def test_build_runs_first(self):
        self.assertEqual(self.order[0], "build")


if __name__ == "__main__":
    unittest.main()
