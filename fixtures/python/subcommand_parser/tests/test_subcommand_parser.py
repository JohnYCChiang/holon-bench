import unittest

from src.argparse_tool.parse import parse

SPEC = {"commands": {"add": {"options": {"--name": {"required": True}, "--force": {"flag": True}}}}}


class SubcommandTest(unittest.TestCase):
    def test_basic(self):
        r = parse(["add", "--name", "x"], SPEC)
        self.assertTrue(r["ok"])
        self.assertEqual(r["command"], "add")
        self.assertEqual(r["options"]["--name"], "x")
        self.assertFalse(r["options"]["--force"])

    def test_missing_required(self):
        r = parse(["add", "--force"], SPEC)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "missing_option")

    def test_unknown_command(self):
        r = parse(["nope"], SPEC)
        self.assertEqual(r["error"]["code"], "unknown_command")


if __name__ == "__main__":
    unittest.main()
