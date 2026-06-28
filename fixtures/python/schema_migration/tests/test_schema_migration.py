import unittest

from src.migrate_tool.migrate import migrate


def _add_email(rec):
    out = dict(rec)
    out["email"] = out["name"] + "@x"
    return out


def _add_active(rec):
    out = dict(rec)
    out["active"] = True
    return out


MIGRATIONS = {1: _add_email, 2: _add_active}


class SchemaMigrationTest(unittest.TestCase):
    def test_multi_step(self):
        rec = {"version": 1, "name": "al"}
        r = migrate(rec, 3, MIGRATIONS)
        self.assertTrue(r["ok"])
        self.assertEqual(r["version"], 3)
        self.assertEqual(r["applied"], [1, 2])
        self.assertEqual(r["record"]["email"], "al@x")
        self.assertEqual(r["record"]["active"], True)

    def test_input_not_mutated(self):
        rec = {"version": 1, "name": "al"}
        migrate(rec, 3, MIGRATIONS)
        self.assertEqual(rec, {"version": 1, "name": "al"})


if __name__ == "__main__":
    unittest.main()
