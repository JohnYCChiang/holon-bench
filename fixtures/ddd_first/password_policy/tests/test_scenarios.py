import unittest

from src.password import PasswordPolicy, Credential


class Passwords(unittest.TestCase):
    def test_valid_password_set(self):
        policy = PasswordPolicy(min_length=8, require_digit=True)
        cred = Credential(policy)
        cred.set_password("hunter42")
        self.assertEqual(cred.password, "hunter42")
        self.assertEqual(cred.events, ["PasswordSet"])

    def test_weak_password_rejected(self):
        policy = PasswordPolicy(min_length=8, require_digit=True)
        cred = Credential(policy)
        with self.assertRaises(ValueError):
            cred.set_password("short")


if __name__ == "__main__":
    unittest.main()
