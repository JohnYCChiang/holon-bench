import unittest

from src.access import AccessControl


class Permissions(unittest.TestCase):
    def test_editor_can_write_not_delete(self):
        ac = AccessControl()
        ac.grant("u", "editor")
        self.assertTrue(ac.can("u", "write"))
        self.assertFalse(ac.can("u", "delete"))

    def test_unknown_role_rejected(self):
        ac = AccessControl()
        with self.assertRaises(ValueError):
            ac.grant("u", "superuser")


class UnknownUser(unittest.TestCase):
    def test_unknown_user_can_do_nothing(self):
        self.assertFalse(AccessControl().can("ghost", "read"))


if __name__ == "__main__":
    unittest.main()
