import unittest

from engine import is_approved, load_quorum


def change(ctype, author, approvals):
    return {"type": ctype, "author": author, "approvals": approvals}


class QuorumTests(unittest.TestCase):
    def setUp(self):
        self.config = load_quorum()

    def test_prod_migration_needs_dba_and_security(self):
        c = change("prod_db_migration", "alice", [
            {"user": "bob", "role": "dba"},
            {"user": "carol", "role": "security"},
        ])
        self.assertTrue(is_approved(self.config, c))

    def test_single_approval_insufficient_for_prod(self):
        c = change("prod_db_migration", "alice", [{"user": "bob", "role": "dba"}])
        self.assertFalse(is_approved(self.config, c))

    def test_code_change_rule_preserved(self):
        c = change("code_change", "dev1", [{"user": "dev1", "role": "eng"}])
        self.assertTrue(is_approved(self.config, c))


if __name__ == "__main__":
    unittest.main()
