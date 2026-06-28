import unittest

from src.idgen_tool.gen import make_id


class DetIdGenTest(unittest.TestCase):
    def test_returns_id_and_namespace(self):
        r = make_id("evt", {"a": 1})
        self.assertTrue(r["ok"])
        self.assertEqual(r["namespace"], "evt")
        self.assertEqual(len(r["id"]), 16)

    def test_stable_for_same_input(self):
        self.assertEqual(make_id("evt", {"a": 1})["id"], make_id("evt", {"a": 1})["id"])

    def test_namespace_changes_id(self):
        self.assertNotEqual(make_id("a", {"x": 1})["id"], make_id("b", {"x": 1})["id"])


if __name__ == "__main__":
    unittest.main()
