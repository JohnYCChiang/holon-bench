import unittest

from src.config_tool.merge import merge_layers


class ConfigMergeTest(unittest.TestCase):
    def test_deep_merge_preserves_sibling_keys(self):
        l1 = {"a": {"x": 1, "y": 2}, "b": 1}
        l2 = {"a": {"y": 9, "z": 3}}
        r = merge_layers([l1, l2])
        self.assertEqual(r["config"], {"a": {"x": 1, "y": 9, "z": 3}, "b": 1})

    def test_inputs_not_mutated(self):
        l1 = {"a": {"x": 1}}
        l2 = {"a": {"y": 2}}
        merge_layers([l1, l2])
        self.assertEqual(l1, {"a": {"x": 1}})
        self.assertEqual(l2, {"a": {"y": 2}})


if __name__ == "__main__":
    unittest.main()
