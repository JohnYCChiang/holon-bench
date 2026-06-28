import unittest

from src.interp_tool.interpolate import interpolate


class EnvInterpTest(unittest.TestCase):
    def test_simple_substitution(self):
        r = interpolate("hi ${NAME}", {"NAME": "bob"})
        self.assertTrue(r["ok"])
        self.assertEqual(r["result"], "hi bob")
        self.assertEqual(r["resolved"], ["NAME"])

    def test_only_referenced_vars_resolved(self):
        r = interpolate("${A}", {"A": "1", "B": "2"})
        self.assertEqual(r["resolved"], ["A"])

    def test_missing_var_is_error(self):
        r = interpolate("${X}", {})
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "unresolved_variable")


if __name__ == "__main__":
    unittest.main()
