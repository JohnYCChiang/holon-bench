import unittest

from src.jsonpatch_tool.apply import apply_patch


class JsonPatchTest(unittest.TestCase):
    def test_replace_existing(self):
        src = {"a": 1}
        r = apply_patch(src, [{"op": "replace", "path": "/a", "value": 2}])
        self.assertTrue(r["ok"])
        self.assertEqual(r["document"], {"a": 2})
        self.assertEqual(src, {"a": 1})

    def test_add_key(self):
        r = apply_patch({"a": 1}, [{"op": "add", "path": "/b", "value": 5}])
        self.assertEqual(r["document"], {"a": 1, "b": 5})

    def test_remove_missing_is_error(self):
        r = apply_patch({"a": 1}, [{"op": "remove", "path": "/z"}])
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
